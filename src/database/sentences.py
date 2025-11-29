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
import concurrent.futures
import time

# Configure logging to suppress verbose OpenAI library logs
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
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
    execute_with_retry,
    execute_with_retry_sync,
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
        if unused_count < 25: # TEMP, WAS 10
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
    logging.info(f"🔄 Starting sentence replenishment for user {user_id}")
    start_time = time.time()
    
    # Get LLM configuration
    llm_config = get_llm_config()
    
    # Check if API key is available
    if not llm_config.api_key:
        logging.error("LLM_API_KEY not found in environment variables, cannot generate sentences")
        return
    
    def generate_sentences():
        """Generate sentences using LLM"""
        # Initialize OpenAI client with instructor patch
        # Since we're already in an async context, we need to get the client synchronously
        llm_config = get_llm_config()
        
        # Check if API key is available
        if not llm_config.api_key:
            raise ValueError("LLM_API_KEY not found in environment variables")
        
        # Create the client directly without async
        import instructor
        from openai import OpenAI
        client = instructor.patch(OpenAI(base_url=llm_config.api_url, api_key=llm_config.api_key))
        
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

Please generate exactly 2 sentences in the format requested.""" # TEMP: WAS 25 SENTENCES
        
        logging.info(f"Connecting to OpenAI API for user {user_id}")
        logging.info(f"Using model: {llm_config.model_name}")
        logging.info("Generating Italian sentences...")
        
        # Call the LLM with structured output
        logging.debug(f"About to call LLM API with model: {llm_config.model_name}")
        logging.debug(f"Response model type: {type(SentenceList)}")
        logging.debug(f"Response model: {SentenceList}")
        
        try:
            # The instructor.patch modifies the client to support response_model parameter
            # In newer versions of instructor, the create method is synchronous, not async
            logging.info(f"🌐 Making LLM API request to {llm_config.api_url} with model {llm_config.model_name}")
            api_start_time = time.time()
            response: SentenceList = client.chat.completions.create(
                model=llm_config.model_name,
                response_model=SentenceList,
                messages=[
                    {"role": "system", "content": system_prompt},
                ]
            )
            api_duration = time.time() - api_start_time
            logging.info(f"🌐 LLM API request completed in {api_duration:.2f} seconds")
            logging.debug(f"LLM API call successful, response type: {type(response)}")
            logging.debug(f"Generated sentences count: {len(response.sentences)}")
            
        except Exception as e:
            # Log concise error message without verbose details
            error_msg = str(e) if len(str(e)) < 100 else f"{str(e)[:100]}..."
            logging.error(f"LLM API call failed: {error_msg}")
            
            # Fallback: try without response_model and parse manually
            logging.info("Falling back to manual parsing approach")
            try:
                logging.info(f"🌐 Making fallback LLM API request to {llm_config.api_url} with model {llm_config.model_name}")
                fallback_start_time = time.time()
                raw_response = client.chat.completions.create(
                    model=llm_config.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                    ]
                )
                fallback_duration = time.time() - fallback_start_time
                logging.info(f"🌐 Fallback LLM API request completed in {fallback_duration:.2f} seconds")
                content = raw_response.choices[0].message.content
                logging.debug(f"Raw response content: {content}")
                
                # Parse the content manually into sentences
                # Assuming the LLM returns sentences separated by newlines or numbered list
                sentences = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line:
                        # Remove numbering if present (e.g., "1. ", "2) ", etc.)
                        import re
                        line = re.sub(r'^\s*\d+[\.\)\-]\s*', '', line)
                        if line:
                            sentences.append(line)
                
                response = SentenceList(sentences=sentences)
                logging.debug(f"Parsed {len(sentences)} sentences manually")
                
            except Exception as e2:
                # Log concise fallback error
                fallback_error = str(e2) if len(str(e2)) < 100 else f"{str(e2)[:100]}..."
                logging.error(f"Fallback approach also failed: {fallback_error}")
                raise
        
        logging.info(f"Generated {len(response.sentences)} sentences from API for user {user_id}")
        return response.sentences
    
    try:
        # Generate sentences with retry logic
        # Run the synchronous LLM calls in a thread pool to avoid blocking the event loop
        logging.info(f"⏳ Starting LLM API call for user {user_id}...")
        llm_start_time = time.time()
        
        # Use a thread pool executor to run the blocking LLM calls
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Run the sync function in a thread
            generated_sentences = await loop.run_in_executor(
                executor,
                execute_with_retry_sync,
                generate_sentences
            )
        
        llm_duration = time.time() - llm_start_time
        logging.info(f"✅ LLM API call completed for user {user_id} in {llm_duration:.2f} seconds")
        
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
            logging.info(f"💾 Starting database storage for user {user_id}...")
            db_start_time = time.time()
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
                
                logging.info(f"✅ Successfully stored {len(valid_sentences)} valid sentences in database for user {user_id}")
                
            finally:
                await conn.close()
                db_duration = time.time() - db_start_time
                logging.info(f"💾 Database storage completed for user {user_id} in {db_duration:.2f} seconds")
    
    except Exception as e:
        # Log concise error message without verbose details
        error_msg = str(e) if len(str(e)) < 100 else f"{str(e)[:100]}..."
        logging.error(f"❌ Failed to generate sentences for user {user_id}: {error_msg}")
    
    finally:
        total_duration = time.time() - start_time
        logging.info(f"🔚 Sentence replenishment completed for user {user_id} in {total_duration:.2f} seconds")