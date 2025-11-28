import asyncpg
import os
from dotenv import load_dotenv
from aiogram.types import User

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "parla_italiano")
DB_USER = os.getenv("DB_USER", "parla_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")

async def get_random_sentence() -> str:
    """Get a random Italian sentence from the database"""
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    try:
        row = await conn.fetchrow("SELECT sentence FROM italian_sentences ORDER BY RANDOM() LIMIT 1")
        return row['sentence'] if row else "Ciao come stai"  # fallback
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
        tables = ['italian_sentences', 'encouraging_phrases', 'error_phrases', 'users']
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