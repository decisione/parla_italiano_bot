"""
Sentence management module for Parla Italiano Bot.

This module handles sentence-related operations including retrieval, result tracking,
and content generation using LLM integration.
"""

import asyncpg
import asyncio
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram.types import User

# Use the same mock config functions from other modules
def get_database_config():
    """Get database configuration, with fallback for testing"""
    try:
        from config import get_database_config as real_get_database_config
        return real_get_database_config()
    except FileNotFoundError:
        # Return mock config for testing when config.ini doesn't exist
        class MockDatabaseConfig:
            host = "localhost"
            port = 5432
            name = "parla_italiano"
            user = "parla_user"
            password = ""
        return MockDatabaseConfig()

def get_llm_config():
    """Get LLM configuration, with fallback for testing"""
    try:
        from config import get_llm_config as real_get_llm_config
        return real_get_llm_config()
    except FileNotFoundError:
        # Return mock config for testing
        class MockLLMConfig:
            api_key = "test-key"
            api_url = "https://test.api"
            model_name = "test-model"
        return MockLLMConfig()
from .base import (
    is_valid_italian_sentence,
    clean_sentence,
    get_llm_client,
    execute_with_retry,
    SentenceList
)


async def get_random_sentence(user_id: int) -> tuple[int | None, str]:
    """Get a random Italian sentence ID and text from the database, preferring sentences the user has not successfully completed"""
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
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
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
    )
    try:
        await conn.execute("""
            INSERT INTO italian_sentences_results (user_id, italian_sentence_id, is_success)
            VALUES ($1, $2, $3)
        """, user_id, sentence_id, is_success)
    finally:
        await conn.close()


async def get_random_encouraging_phrase() -> str:
    """Get a random encouraging phrase from the database"""
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
    )
    try:
        row = await conn.fetchrow("SELECT phrase FROM encouraging_phrases ORDER BY RANDOM() LIMIT 1")
        return row['phrase'] if row else "Bravo!"  # fallback
    finally:
        await conn.close()


async def get_random_error_phrase() -> str:
    """Get a random error phrase from the database"""
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
    )
    try:
        row = await conn.fetchrow("SELECT phrase FROM error_phrases ORDER BY RANDOM() LIMIT 1")
        return row['phrase'] if row else "Quasi!"  # fallback
    finally:
        await conn.close()


async def sentence_replenishment(user_id: int) -> None:
    """Generate Italian sentences using OpenAI API and store them in the database"""
    logging.info(f"Starting sentence replenishment for user {user_id}")
    
    # Get LLM configuration
    llm_config = get_llm_config()
    
    # Check if API key is available
    if not llm_config.api_key:
        logging.error("LLM_API_KEY not found in environment variables, cannot generate sentences")
        return
    
    async def generate_sentences():
        """Generate sentences using LLM"""
        # Initialize OpenAI client with instructor patch
        client = await get_llm_client()
        
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
        
        logging.info(f"Connecting to OpenAI API for user {user_id}")
        logging.info(f"Using model: {llm_config.model_name}")
        logging.info("Generating Italian sentences...")
        
        # Call the LLM with structured output
        response: SentenceList = await client.chat.completions.create(
            model=llm_config.model_name,
            response_model=SentenceList,
            messages=[
                {"role": "system", "content": system_prompt},
            ]
        )
        
        logging.info(f"Generated {len(response.sentences)} sentences from API for user {user_id}")
        return response.sentences
    
    try:
        # Generate sentences with retry logic
        generated_sentences = await execute_with_retry(generate_sentences)
        
        # Validate and clean sentences
        valid_sentences = []
        invalid_sentences = []
        
        for i, sentence in enumerate(generated_sentences, 1):
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
            db_config = get_database_config()
            conn = await asyncpg.connect(
                host=db_config.host, port=db_config.port, database=db_config.name,
                user=db_config.user, password=db_config.password
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
    
    except Exception as e:
        logging.error(f"Failed to generate sentences for user {user_id}: {e}")