"""
Database connection management module for Parla Italiano Bot.

This module handles database connections, migrations, and basic database operations.
"""

import asyncpg
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock config for testing if config.ini doesn't exist
class MockDatabaseConfig:
    host = "localhost"
    port = 5432
    name = "parla_italiano"
    user = "parla_user"
    password = ""

def get_database_config():
    """Get database configuration, with fallback for testing"""
    try:
        from config import get_database_config as real_get_database_config
        return real_get_database_config()
    except FileNotFoundError:
        # Return mock config for testing when config.ini doesn't exist
        return MockDatabaseConfig()


async def get_schema_migrations():
    """Get all schema migrations for logging"""
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
    )
    try:
        rows = await conn.fetch("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at")
        return [f"{row['version']} applied at {row['applied_at']}" for row in rows]
    finally:
        await conn.close()


async def get_table_counts():
    """Get row counts for all content tables"""
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
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