"""
User management module for Parla Italiano Bot.

This module handles user profile operations including creation, updates, and access tracking.
"""

import asyncpg
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram.types import User

# Use the same mock config function from connection.py
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


async def get_or_create_user(user: User) -> int:
    """Get or create user record. Updates profile fields and last_access_at if exists, inserts with first_access_at if new."""
    db_config = get_database_config()
    conn = await asyncpg.connect(
        host=db_config.host, port=db_config.port, database=db_config.name,
        user=db_config.user, password=db_config.password
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