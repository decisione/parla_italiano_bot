"""Unit tests for database functions (mocked asyncpg, no live DB required)"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from aiogram.types import User
from src.database import get_or_create_user, get_table_counts

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_get_table_counts_includes_users(mock_connect):
    """Test get_table_counts includes 'users' and fetches count."""
    mock_conn = AsyncMock()
    
    # Set up fetchrow to return dictionaries with count values
    mock_conn.fetchrow.side_effect = [
        {'count': 10},    # italian_sentences
        {'count': 20},    # encouraging_phrases
        {'count': 15},    # error_phrases
        {'count': 42}     # users
    ]
    
    # Set up the connection mock to be returned by asyncpg.connect()
    mock_connect.return_value = mock_conn

    counts = await get_table_counts()
    assert 'users' in counts
    assert counts['users'] == 42
    assert mock_conn.fetchrow.call_count == 4
    mock_conn.fetchrow.assert_any_call("SELECT COUNT(*) as count FROM users")

@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_get_or_create_user_new_insert(mock_connect):
    """Test insert path for new user."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None  # New user
    mock_connect.return_value = mock_conn

    user = User(id=12345, first_name="NewTest", is_bot=False, is_premium=True)
    result = await get_or_create_user(user)
    assert result == 12345
    mock_conn.fetchrow.assert_called_once()
    mock_conn.execute.assert_called_once()
    # Verify INSERT called with expected args (NOW() auto)
    call_args = mock_conn.execute.call_args[0]
    assert call_args[1] == 12345  # user.id
    assert call_args[2] == "NewTest"  # user.first_name

@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_get_or_create_user_existing_update(mock_connect):
    """Test update path for existing user."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {'user_id': 12345}  # Exists
    mock_connect.return_value = mock_conn

    user = User(id=12345, first_name="UpdatedTest", username="testuser", is_bot=False)
    result = await get_or_create_user(user)
    assert result == 12345
    mock_conn.execute.assert_called_once()
    # Verify UPDATE called (NOW() for last_access_at)
    call_args = mock_conn.execute.call_args[0]
    assert call_args[1] == 12345  # user.id
    assert call_args[2] == "UpdatedTest"  # user.first_name
    assert call_args[4] == "testuser"  # user.username