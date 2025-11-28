import asyncpg
import asyncio
import os
from dotenv import load_dotenv
from aiogram.types import User

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "parla_italiano")
DB_USER = os.getenv("DB_USER", "parla_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")

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


async def sentence_replenishment(user_id: int) -> None:
    """Placeholder for sentence replenishment (1 min delay)."""
    await asyncio.sleep(60)
    # TODO: Implement actual sentence replenishment logic


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