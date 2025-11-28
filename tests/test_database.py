"""Unit tests for database functions (mocked asyncpg, no live DB required)"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from aiogram.types import User
from src.database import get_or_create_user, get_table_counts, get_random_sentence, store_sentence_result

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_get_table_counts_all_tables(mock_connect):
    """Test get_table_counts includes all content tables including results."""
    mock_conn = AsyncMock()
    
    # Set up fetchrow to return dictionaries with count values
    mock_conn.fetchrow.side_effect = [
        {'count': 10},    # italian_sentences
        {'count': 20},    # encouraging_phrases
        {'count': 15},    # error_phrases
        {'count': 42},    # users
        {'count': 5}      # italian_sentences_results
    ]
    
    # Set up the connection mock to be returned by asyncpg.connect()
    mock_connect.return_value = mock_conn

    counts = await get_table_counts()
    assert 'users' in counts
    assert counts['users'] == 42
    assert 'italian_sentences_results' in counts
    assert counts['italian_sentences_results'] == 5
    assert mock_conn.fetchrow.call_count == 5
    mock_conn.fetchrow.assert_any_call("SELECT COUNT(*) as count FROM users")
    mock_conn.fetchrow.assert_any_call("SELECT COUNT(*) as count FROM italian_sentences_results")

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
@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_get_random_sentence_prefer_uncompleted(mock_connect):
    """Test get_random_sentence prefers uncompleted sentences."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [{'id': 123, 'sentence': 'Test uncompleted sentence'}]
    mock_connect.return_value = mock_conn

    result = await get_random_sentence(123)
    assert result == (123, 'Test uncompleted sentence')
    assert mock_conn.fetchrow.call_count == 1


@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_get_random_sentence_fallback_to_random(mock_connect):
    """Test fallback to random sentence when no uncompleted available."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [None, {'id': 456, 'sentence': 'Fallback sentence'}]
    mock_connect.return_value = mock_conn

    result = await get_random_sentence(123)
    assert result == (456, 'Fallback sentence')
    assert mock_conn.fetchrow.call_count == 2


@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_get_random_sentence_no_sentences(mock_connect):
    """Test fallback when no sentences at all."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [None, None]
    mock_connect.return_value = mock_conn

    result = await get_random_sentence(123)
    assert result == (None, "Ciao come stai")
    assert mock_conn.fetchrow.call_count == 2


@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_store_sentence_result(mock_connect):
    """Test store_sentence_result inserts correctly."""
    mock_conn = AsyncMock()
    mock_connect.return_value = mock_conn

    await store_sentence_result(12345, 678, True)

    mock_conn.execute.assert_called_once()
    args = mock_conn.execute.call_args[0]
    query = args[0]
    params = args[1:]
    assert "INSERT INTO italian_sentences_results" in query
    assert params == (12345, 678, True)


@pytest.mark.asyncio
@patch('src.database.asyncpg.connect')
async def test_store_sentence_result_false(mock_connect):
    """Test store_sentence_result with failure."""
    mock_conn = AsyncMock()
    mock_connect.return_value = mock_conn

    await store_sentence_result(12345, 678, False)

    mock_conn.execute.assert_called_once()
    args = mock_conn.execute.call_args[0]
    query = args[0]
    params = args[1:]
    assert params == (12345, 678, False)