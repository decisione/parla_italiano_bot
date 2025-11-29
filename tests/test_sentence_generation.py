"""Unit tests for sentence generation functionality"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.database.sentences import sentence_replenishment
from src.database.base import SentenceList

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
@patch('src.database.sentences.get_llm_config')
@patch('src.database.sentences.get_database_config')
@patch('src.database.sentences.execute_with_retry_sync')
@patch('src.database.sentences.asyncpg.connect')
async def test_sentence_replenishment_success(mock_llm_config, mock_db_config, mock_retry, mock_connect):
    """Test successful sentence replenishment"""
    # Setup mocks
    mock_llm_config.return_value.api_key = "test-key"
    mock_llm_config.return_value.model_name = "test-model"
    mock_llm_config.return_value.api_url = "https://test.api"
    
    mock_db_config.return_value.host = "localhost"
    mock_db_config.return_value.port = 5432
    mock_db_config.return_value.name = "test_db"
    mock_db_config.return_value.user = "test_user"
    mock_db_config.return_value.password = "test_pass"
    
    # Mock retry function to return sentences directly
    mock_retry.return_value = [
        "Questa è una frase di test.",
        "Un'altra frase italiana.",
        "Terza frase di esempio."
    ]
    
    # Mock database connection
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None  # No existing sentence
    mock_connect.return_value = mock_conn
    
    # Test
    user_id = 12345
    await sentence_replenishment(user_id)
    
    # Verify - function should complete without raising exceptions
    # The actual database operations are complex to mock properly

@pytest.mark.asyncio
@patch('src.database.sentences.get_llm_config')
async def test_sentence_replenishment_no_api_key(mock_llm_config):
    """Test sentence replenishment when no API key is available"""
    mock_llm_config.return_value.api_key = None
    
    user_id = 12345
    await sentence_replenishment(user_id)  # Should return early without error

@pytest.mark.asyncio
@patch('src.database.sentences.get_llm_config')
@patch('src.database.sentences.get_database_config')
@patch('src.database.sentences.execute_with_retry_sync')
@patch('src.database.sentences.asyncpg.connect')
async def test_sentence_replenishment_with_duplicates(mock_connect, mock_retry, mock_db_config, mock_llm_config):
    """Test sentence replenishment with duplicate sentences"""
    # Setup mocks
    mock_llm_config.return_value.api_key = "test-key"
    mock_llm_config.return_value.model_name = "test-model"
    mock_llm_config.return_value.api_url = "https://test.api"
    
    mock_db_config.return_value.host = "localhost"
    mock_db_config.return_value.port = 5432
    mock_db_config.return_value.name = "test_db"
    mock_db_config.return_value.user = "test_user"
    mock_db_config.return_value.password = "test_pass"
    
    # Mock retry function to return sentences directly
    mock_retry.return_value = [
        "Questa è una frase di test.",
        "Un'altra frase italiana.",
        "Terza frase di esempio."
    ]
    
    # Mock database connection - first sentence exists, others don't
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [
        {'id': 1},  # First sentence exists
        None,       # Second sentence doesn't exist
        None        # Third sentence doesn't exist
    ]
    mock_connect.return_value = mock_conn
    
    # Test
    user_id = 12345
    await sentence_replenishment(user_id)
    
    # Verify - should only insert the non-duplicate sentences
    assert mock_conn.execute.call_count == 2  # Only for non-existing sentences
    mock_conn.close.assert_called_once()

@pytest.mark.asyncio
@patch('src.database.sentences.get_llm_config')
@patch('src.database.sentences.get_database_config')
@patch('src.database.sentences.execute_with_retry_sync')
async def test_sentence_replenishment_llm_error(mock_retry, mock_db_config, mock_llm_config):
    """Test sentence replenishment when LLM generation fails"""
    mock_llm_config.return_value.api_key = "test-key"
    mock_llm_config.return_value.model_name = "test-model"
    mock_llm_config.return_value.api_url = "https://test.api"
    
    mock_db_config.return_value.host = "localhost"
    mock_db_config.return_value.port = 5432
    mock_db_config.return_value.name = "test_db"
    mock_db_config.return_value.user = "test_user"
    mock_db_config.return_value.password = "test_pass"
    
    # Mock retry function to raise exception
    mock_retry.side_effect = Exception("LLM API error")
    
    user_id = 12345
    # Should not raise exception, just log the error
    await sentence_replenishment(user_id)