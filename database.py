import asyncpg
import os
from dotenv import load_dotenv

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