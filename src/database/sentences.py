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
    is_valid_russian_sentence,
    clean_sentence,
    execute_with_retry,
    execute_with_retry_sync,
    SentenceList,
    SentenceTranslationList
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
#        if 1==1: # TEMPORARY: only for manual testing
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

async def get_random_exercise_prompt() -> str:
    """Get a random exercise prompt from the database"""
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
    )
    try:
        row = await conn.fetchrow("SELECT prompt FROM exercise_prompts ORDER BY RANDOM() LIMIT 1")
        return row['prompt'] if row else "Prossimo!"  # fallback
    finally:
        await conn.close()


async def sentence_replenishment(user_id: int) -> None:
    """Generate Italian sentences with Russian translations using OpenAI API and store them in the database"""
    logging.info(f"🔄 Starting sentence replenishment for user {user_id}")
    start_time = time.time()
    
    # Get LLM configuration
    llm_config = get_llm_config()
    
    # Check if API key is available
    if not llm_config.api_key:
        logging.error("LLM_API_KEY not found in environment variables, cannot generate sentences")
        return
    
    def generate_sentences_with_translations():
        """Generate sentences with Russian translations using LLM"""
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
        system_prompt = """Generate Italian sentences with Russian translations for language learning.
Each entry should include:
1. An Italian sentence that:
   - Is in Italian (not translated from English)
   - Contains 3 to 10 words
   - Is grammatically correct
   - Uses various and different topics
   - Make some of them fun! Make some jokes!
   - Uses standard Italian characters including accented vowels (à, è, é, ì, í, î, ò, ó, ù, ú)
2. A Russian translation that:
   - Is a proper Russian translation of the Italian sentence
   - Uses standard Russian characters including punctuation
   - Is grammatically correct

Examples of appropriate entries:
- Italian: "L'unico mobile presente nella stanza era il nonno." | Russian: "Единственной мебелью в комнате был дедушка."
- Italian: "Questa stanza è troppo costosa, dormirò per strada." | Russian: "Этот номер слишком дорогой, я буду спать на улице."
- Italian: "Perché non ti piace Marco, ha la barba?" | Russian: "Почему тебе не нравится Марко, у него же есть борода?"

Please generate from 25 to 35 sentence pairs in the format requested."""
        
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
            response: SentenceTranslationList = client.chat.completions.create(
                model=llm_config.model_name,
                response_model=SentenceTranslationList,
                messages=[
                    {"role": "system", "content": system_prompt},
                ]
            )
            api_duration = time.time() - api_start_time
            logging.info(f"🌐 LLM API request completed in {api_duration:.2f} seconds")
            logging.debug(f"LLM API call successful, response type: {type(response)}")
            logging.debug(f"Generated sentence pairs count: {len(response.sentences)}")
            
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
                
                # Parse the content manually into sentence pairs
                # Assuming the LLM returns sentences in format: "Italian: ... | Russian: ..."
                sentence_pairs = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line:
                        # Try to parse Italian/Russian pairs
                        import re
                        italian_match = re.search(r'Italian:\s*(.+?)(?:\s*\|\s*Russian:|$)', line, re.IGNORECASE)
                        russian_match = re.search(r'Russian:\s*(.+?)(?:\s*\||$)', line, re.IGNORECASE)
                        
                        if italian_match and russian_match:
                            italian_sentence = italian_match.group(1).strip()
                            russian_sentence = russian_match.group(1).strip()
                            # Remove quotes if present
                            italian_sentence = italian_sentence.strip('"\'')
                            russian_sentence = russian_sentence.strip('"\'')
                            if italian_sentence and russian_sentence:
                                sentence_pairs.append({
                                    'italian': italian_sentence,
                                    'russian': russian_sentence
                                })
                
                # Convert to SentenceTranslationList format
                response = SentenceTranslationList(sentences=[
                    type('SentenceWithTranslation', (), {'italian': pair['italian'], 'russian': pair['russian']})
                    for pair in sentence_pairs
                ])
                logging.debug(f"Parsed {len(sentence_pairs)} sentence pairs manually")
                
            except Exception as e2:
                # Log concise fallback error
                fallback_error = str(e2) if len(str(e2)) < 100 else f"{str(e2)[:100]}..."
                logging.error(f"Fallback approach also failed: {fallback_error}")
                raise
        
        logging.info(f"Generated {len(response.sentences)} sentence pairs from API for user {user_id}")
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
            generated_sentence_pairs = await loop.run_in_executor(
                executor,
                execute_with_retry_sync,
                generate_sentences_with_translations
            )
        
        llm_duration = time.time() - llm_start_time
        logging.info(f"✅ LLM API call completed for user {user_id} in {llm_duration:.2f} seconds")
        
        # Validate and clean sentences
        valid_sentence_pairs = []
        invalid_sentence_pairs = []
        
        for i, sentence_pair in enumerate(generated_sentence_pairs, 1):
            # Handle both object and dict formats
            if hasattr(sentence_pair, 'italian') and hasattr(sentence_pair, 'russian'):
                italian_sentence = sentence_pair.italian
                russian_sentence = sentence_pair.russian
            elif isinstance(sentence_pair, dict):
                italian_sentence = sentence_pair.get('italian', '')
                russian_sentence = sentence_pair.get('russian', '')
            else:
                invalid_sentence_pairs.append((i, str(sentence_pair)))
                continue
            
            cleaned_italian = clean_sentence(italian_sentence)
            cleaned_russian = clean_sentence(russian_sentence)
            
            # Validate both Italian and Russian sentences
            if (is_valid_italian_sentence(cleaned_italian) and
                is_valid_russian_sentence(cleaned_russian)):
                valid_sentence_pairs.append({
                    'italian': cleaned_italian,
                    'russian': cleaned_russian
                })
                logging.debug(f"Valid sentence pair {i}: '{cleaned_italian}' | '{cleaned_russian}'")
            else:
                invalid_sentence_pairs.append((i, cleaned_italian, cleaned_russian))
                logging.debug(f"Invalid sentence pair {i}: '{cleaned_italian}' | '{cleaned_russian}'")
        
        logging.info(f"Validation Results for user {user_id}:")
        logging.info(f"Valid sentence pairs: {len(valid_sentence_pairs)}")
        logging.info(f"Invalid sentence pairs: {len(invalid_sentence_pairs)}")
        
        if invalid_sentence_pairs:
            logging.info("Invalid sentence pairs details:")
            for i, italian, russian in invalid_sentence_pairs:
                logging.info(f"  Pair {i}: '{italian}' | '{russian}'")
        
        # Store valid sentences in the database
        if valid_sentence_pairs:
            logging.info(f"💾 Starting database storage for user {user_id}...")
            db_start_time = time.time()
            db_config = get_database_config()
            conn = await asyncpg.connect(
                host=db_config.host, port=db_config.port, database=db_config.name,
                user=db_config.user, password=db_config.password
            )
            try:
                for pair in valid_sentence_pairs:
                    italian_sentence = pair['italian']
                    russian_sentence = pair['russian']
                    
                    # Check if sentence already exists to avoid duplicates
                    existing = await conn.fetchrow(
                        "SELECT id FROM italian_sentences WHERE sentence = $1",
                        italian_sentence
                    )
                    if not existing:
                        await conn.execute(
                            "INSERT INTO italian_sentences (sentence, sentence_rus) VALUES ($1, $2)",
                            italian_sentence, russian_sentence
                        )
                        logging.debug(f"Added sentence pair to database: '{italian_sentence}' | '{russian_sentence}'")
                    else:
                        logging.debug(f"Skipped duplicate sentence: '{italian_sentence}'")
                
                logging.info(f"✅ Successfully stored {len(valid_sentence_pairs)} valid sentence pairs in database for user {user_id}")
                
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