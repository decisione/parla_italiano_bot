"""
Tests for the stats command handler.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from aiogram.types import Message, User

# Add the project root to Python path for imports
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.bot_commands.stats import create_stats_command_handler


@pytest.mark.asyncio
async def test_stats_command_handler():
    """Test that the stats command handler works correctly"""
    
    # Mock message and user
    mock_user = User(id=12345, first_name="Test", last_name="User", username="testuser", is_bot=False, language_code="it")
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = mock_user
    mock_message.answer = AsyncMock()
    
    # Mock the database functions
    with patch('src.bot_commands.stats.get_or_create_user') as mock_get_user, \
         patch('src.bot_commands.stats.get_stats_data') as mock_get_stats:
        
        # Setup mock return values
        mock_get_user.return_value = 12345
        mock_get_stats.return_value = {
            'total_users': 10,
            'total_sentences': 50,
            'total_attempts': 100,
            'global_success_rate': 75.5,
            'user_success_rate': 80.0
        }
        
        # Create and call the handler
        handler = create_stats_command_handler()
        await handler(mock_message)
        
        # Verify the functions were called
        mock_get_user.assert_called_once_with(mock_user)
        mock_get_stats.assert_called_once_with(12345)
        
        # Verify the response was sent
        mock_message.answer.assert_called_once()
        response_text = mock_message.answer.call_args[0][0]
        
        # Check that all required statistics are in the response
        assert "📊 Statistiche del Bot" in response_text
        assert "👥 Utenti totali: 10" in response_text
        assert "📝 Frasi totali: 50 (aggiunto automaticamente se necessario)" in response_text
        assert "🎯 Tentativi totali: 100" in response_text
        assert "📈 Tasso di successo globale: 75.5%" in response_text
        assert "🎯 Tasso di successo personale: 80.0%" in response_text


@pytest.mark.asyncio
async def test_stats_command_handler_zero_attempts():
    """Test stats command when there are no attempts yet"""
    
    # Mock message and user
    mock_user = User(id=12345, first_name="Test", last_name="User", username="testuser", is_bot=False, language_code="it")
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = mock_user
    mock_message.answer = AsyncMock()
    
    # Mock the database functions with zero attempts
    with patch('src.bot_commands.stats.get_or_create_user') as mock_get_user, \
         patch('src.bot_commands.stats.get_stats_data') as mock_get_stats:
        
        # Setup mock return values
        mock_get_user.return_value = 12345
        mock_get_stats.return_value = {
            'total_users': 5,
            'total_sentences': 25,
            'total_attempts': 0,
            'global_success_rate': 0.0,
            'user_success_rate': 0.0
        }
        
        # Create and call the handler
        handler = create_stats_command_handler()
        await handler(mock_message)
        
        # Verify the response was sent
        mock_message.answer.assert_called_once()
        response_text = mock_message.answer.call_args[0][0]
        
        # Check that all required statistics are in the response
        assert "📊 Statistiche del Bot" in response_text
        assert "👥 Utenti totali: 5" in response_text
        assert "📝 Frasi totali: 25 (aggiunto automaticamente se necessario)" in response_text
        assert "🎯 Tentativi totali: 0" in response_text
        assert "📈 Tasso di successo globale: 0.0%" in response_text
        assert "🎯 Tasso di successo personale: 0.0%" in response_text