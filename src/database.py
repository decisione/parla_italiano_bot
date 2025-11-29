import asyncpg
import asyncio
import os
import re
import logging
import random
import time
from typing import List
from dotenv import load_dotenv
from aiogram.types import User
import pydantic
from openai import OpenAI
import instructor

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "parla_italiano")
DB_USER = os.getenv("DB_USER", "parla_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Configuration for OpenAI API
API_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv("API_KEY")
MODEL_NAME = "qwen/qwen3-235b-a22b:free"

# Italian character set including accented vowels
ITALIAN_CHARACTERS = set('abcdefghiklmnopqrstuvzàèéìíîòóùú .,;:!?\'-')

# SETUP

async def get_schema_migrations():
    """Get all schema migrations for logging"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        rows = await conn.fetch("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at")
        return [f"{row['version']} applied at {row['applied_at']}" for row in rows]
    finally:
        await conn.close()


async def get_table_counts():
    """Get row counts for all content tables"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        counts = {}
        tables = ['italian_sentences', 'encouraging_phrases', 'error_phrases', 'users', 'italian_sentences_results']
        for table in tables:
            row = await conn.fetchrow(f"SELECT COUNT(*) as count FROM {table}")
            counts[table] = row['count']
        return counts
    finally:
        await conn.close()


async def get_or_create_user(user: User) -> int:
    """Get or create user record. Updates profile fields and last_access_at if exists, inserts with first_access_at if new."""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        # Check if user exists
        row = await conn.fetchrow("SELECT user_id FROM users WHERE user_id = $1", user.id)
        if row:
            # Update existing user profile and last access
            await conn.execute("""
                UPDATE users SET
                    first_name = $2,
                    last_name = $3,
                    username = $4,
                    language_code = $5,
                    is_bot = $6,
                    is_premium = $7,
                    last_access_at = NOW()
                WHERE user_id = $1
            """, user.id, user.first_name, user.last_name, user.username, user.language_code, user.is_bot, user.is_premium)
        else:
            # Create new user
            await conn.execute("""
                INSERT INTO users (
                    user_id, first_name, last_name, username, language_code,
                    is_bot, is_premium, first_access_at, last_access_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
            """, user.id, user.first_name, user.last_name, user.username, user.language_code, user.is_bot, user.is_premium)
        return user.id
    finally:
        await conn.close()


# COMMON

async def get_random_encouraging_phrase() -> str:
    """Get a random encouraging phrase from the database"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        row = await conn.fetchrow("SELECT phrase FROM encouraging_phrases ORDER BY RANDOM() LIMIT 1")
        return row['phrase'] if row else "Bravo!"  # fallback
    finally:
        await conn.close()


async def get_random_error_phrase() -> str:
    """Get a random error phrase from the database"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        row = await conn.fetchrow("SELECT phrase FROM error_phrases ORDER BY RANDOM() LIMIT 1")
        return row['phrase'] if row else "Quasi!"  # fallback
    finally:
        await conn.close()


# SENTENCES

async def get_random_sentence(user_id: int) -> tuple[int | None, str]:
    """Get a random Italian sentence ID and text from the database, preferring sentences the user has not successfully completed"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        # Check remaining uncompleted count for replenishment
        count_row = await conn.fetchrow("""
            SELECT COUNT(*) as unused_count FROM italian_sentences
            WHERE id NOT IN (
                SELECT italian_sentence_id FROM italian_sentences_results
                WHERE user_id = $1 AND is_success = true
            )
        """, user_id)
        unused_count = count_row['unused_count'] if count_row else 0
        if unused_count < 10:
            asyncio.create_task(sentence_replenishment(user_id))

        # Prefer sentences not successfully completed by this user
        row = await conn.fetchrow("""
            SELECT id, sentence FROM italian_sentences
            WHERE id NOT IN (
                SELECT italian_sentence_id FROM italian_sentences_results
                WHERE user_id = $1 AND is_success = true
            )
            ORDER BY RANDOM() LIMIT 1
        """, user_id)
        if row:
            return row['id'], row['sentence']

        # Fallback to any random sentence
        row = await conn.fetchrow("SELECT id, sentence FROM italian_sentences ORDER BY RANDOM() LIMIT 1")
        if row:
            return row['id'], row['sentence']
        return None, "Ciao come stai"  # fallback
    finally:
        await conn.close()


async def store_sentence_result(user_id: int, sentence_id: int, is_success: bool) -> None:
    """Store a sentence result for a user"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        await conn.execute("""
            INSERT INTO italian_sentences_results (user_id, italian_sentence_id, is_success)
            VALUES ($1, $2, $3)
        """, user_id, sentence_id, is_success)
    finally:
        await conn.close()


# Pydantic model for structured output
class SentenceList(pydantic.BaseModel):
    sentences: List[str]

def is_valid_italian_sentence(sentence: str) -> bool:
    """
    Validate that a sentence:
    1. Contains only Italian letters (including accented characters)
    2. Has between 3 and 10 words
    3. Does not contain duplicate words
    """
    # Check word count
    word_count = len(sentence.split())
    if word_count < 3 or word_count > 10:
        return False
    
    # Check for duplicate words
    words = sentence.lower().split()
    if len(words) != len(set(words)):
        return False
    
    # Check character set
    sentence_lower = sentence.lower()
    for char in sentence_lower:
        if char not in ITALIAN_CHARACTERS:
            return False
    
    return True

def clean_sentence(sentence: str) -> str:
    """Clean and normalize sentence"""
    # Remove extra whitespace and normalize
    return ' '.join(sentence.strip().split())

async def sentence_replenishment(user_id: int) -> None:
    """Generate Italian sentences using OpenAI API and store them in the database"""
    logging.info(f"Starting sentence replenishment for user {user_id}")
    
    # Check if API key is available
    if not API_KEY:
        logging.error("API_KEY not found in environment variables, cannot generate sentences")
        return
    
    max_retries = 5
    base_delay = 1  # Base delay in seconds
    
    for attempt in range(max_retries):
        try:
            # Initialize OpenAI client with instructor patch
            client = instructor.patch(OpenAI(base_url=API_URL, api_key=API_KEY))
            
            # System prompt to guide the LLM
            system_prompt = """Generate Italian sentences for language learning.
Each sentence should:
- Be in Italian (not translated from English)
- Contain 3 to 10 words
- Be grammatically correct
- Use various and different topics
- Make some of them fun! Make some jokes!
- Use standard Italian characters including accented vowels (à, è, é, ì, í, î, ò, ó, ù, ú)

Examples of appropriate sentences:
- "L'unico mobile presente nella stanza era il nonno."
- "Questa stanza è troppo costosa, dormirò per strada."
- "Perché non ti piace Marco, ha la barba?"

Please generate exactly 25 sentences in the format requested."""
            
            logging.info(f"Connecting to OpenAI API for user {user_id} (attempt {attempt + 1}/{max_retries})")
            logging.info(f"Using model: {MODEL_NAME}")
            logging.info("Generating Italian sentences...")
            
            # Call the LLM with structured output
            response: SentenceList = client.chat.completions.create(
                model=MODEL_NAME,
                response_model=SentenceList,
                messages=[
                    {"role": "system", "content": system_prompt},
                ]
            )
            
            # If we reach this point, the request was successful
            logging.info(f"Generated {len(response.sentences)} sentences from API for user {user_id}")
            
            # Validate and clean sentences
            valid_sentences = []
            invalid_sentences = []
            
            for i, sentence in enumerate(response.sentences, 1):
                cleaned = clean_sentence(sentence)
                
                if is_valid_italian_sentence(cleaned):
                    valid_sentences.append(cleaned)
                    logging.debug(f"Valid sentence {i}: '{cleaned}'")
                else:
                    invalid_sentences.append((i, cleaned))
                    word_count = len(cleaned.split())
                    logging.debug(f"Invalid sentence {i}: '{cleaned}'")
            
            logging.info(f"Validation Results for user {user_id}:")
            logging.info(f"Valid sentences: {len(valid_sentences)}")
            logging.info(f"Invalid sentences: {len(invalid_sentences)}")
            
            if invalid_sentences:
                logging.info("Invalid sentences details:")
                for i, sentence in invalid_sentences:
                    logging.info(f"  Sentence {i}: '{sentence}'")
            
            # Store valid sentences in the database
            if valid_sentences:
                conn = await asyncpg.connect(
                    host=DB_HOST, port=DB_PORT, database=DB_NAME,
                    user=DB_USER, password=DB_PASSWORD
                )
                try:
                    for sentence in valid_sentences:
                        # Check if sentence already exists to avoid duplicates
                        existing = await conn.fetchrow(
                            "SELECT id FROM italian_sentences WHERE sentence = $1",
                            sentence
                        )
                        if not existing:
                            await conn.execute(
                                "INSERT INTO italian_sentences (sentence) VALUES ($1)",
                                sentence
                            )
                            logging.debug(f"Added sentence to database: '{sentence}'")
                        else:
                            logging.debug(f"Skipped duplicate sentence: '{sentence}'")
                    
                    logging.info(f"Successfully stored {len(valid_sentences)} valid sentences in database for user {user_id}")
                    
                finally:
                    await conn.close()
            
            # Success - break out of retry loop
            break
            
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed for user {user_id}: {e}")
            
            # Check if it's a rate limit error (429)
            if hasattr(e, 'status_code') and e.status_code == 429:
                if attempt < max_retries - 1:  # Don't wait on the last attempt
                    # Wait a random amount of time between base_delay and base_delay * 2^attempt
                    wait_time = random.uniform(base_delay, base_delay * (2 ** attempt))
                    logging.info(f"Rate limited. Waiting {wait_time:.2f} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logging.error(f"Rate limit exceeded after {max_retries} attempts for user {user_id}")
                    return
            else:
                if attempt < max_retries - 1:  # Don't wait on the last attempt
                    # Wait before retrying for other types of errors
                    wait_time = random.uniform(base_delay, base_delay * (2 ** attempt))
                    logging.info(f"Waiting {wait_time:.2f} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logging.error(f"Failed to generate sentences after {max_retries} attempts for user {user_id}: {e}")
                    return
