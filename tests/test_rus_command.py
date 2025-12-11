"""
Unit tests for the /rus command handler
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram.types import Message, User
from src.bot_commands.rus import create_rus_command_handler


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@patch('src.bot_commands.rus.get_or_create_user')
@patch('src.bot_commands.rus.get_last_attempted_sentence')
async def test_rus_command_with_translation(mock_get_last, mock_get_or_create):
    """Test /rus command when user has a sentence with Russian translation"""
    # Setup mocks
    mock_get_or_create.return_value = None  # No return value expected
    
    mock_get_last.return_value = {
        'italian': 'Questa è una frase di test.',
        'russian': 'Это тестовое предложение.'
    }
    
    # Create mock message
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = User(id=12345, first_name="Test", is_bot=False, language_code="en")
    mock_message.answer = AsyncMock()
    
    # Create handler and test
    from src.state.learning_state import LearningState
    learning_state = LearningState()
    mock_bot = AsyncMock()
    handler = create_rus_command_handler(learning_state, mock_bot)
    await handler(mock_message)
    
    # Verify
    mock_get_or_create.assert_called_once()
    mock_get_last.assert_called_once_with(12345)
    mock_message.answer.assert_called_once()
    
    # Check the message content
    call_args = mock_message.answer.call_args
    message_text = call_args[0][0]
    assert "🔤 <b>Traduzione italiana-russo</b>" in message_text
    assert "Questa è una frase di test." in message_text
    assert "Это тестовое предложение." in message_text


@pytest.mark.asyncio
@patch('src.bot_commands.rus.get_or_create_user')
@patch('src.bot_commands.rus.get_last_attempted_sentence')
async def test_rus_command_no_translation(mock_get_last, mock_get_or_create):
    """Test /rus command when user has a sentence but no Russian translation"""
    # Setup mocks
    mock_get_or_create.return_value = None
    mock_get_last.return_value = {
        'italian': 'Questa è una frase di test.',
        'russian': ''  # Empty translation
    }
    
    # Create mock message
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = User(id=12345, first_name="Test", is_bot=False, language_code="en")
    mock_message.answer = AsyncMock()
    
    # Create handler and test
    from src.state.learning_state import LearningState
    learning_state = LearningState()
    mock_bot = AsyncMock()
    handler = create_rus_command_handler(learning_state, mock_bot)
    await handler(mock_message)
    
    # Verify
    mock_get_or_create.assert_called_once()
    mock_get_last.assert_called_once_with(12345)
    mock_message.answer.assert_called_once()
    
    # Check the message content
    call_args = mock_message.answer.call_args
    message_text = call_args[0][0]
    assert "🔤 <b>Traduzione italiana-russo</b>" in message_text
    assert "Traduzione non disponibile ancora" in message_text
    assert "Continua a giocare per sbloccare le traduzioni!" in message_text


@pytest.mark.asyncio
@patch('src.bot_commands.rus.get_or_create_user')
@patch('src.bot_commands.rus.get_last_attempted_sentence')
async def test_rus_command_no_sentences(mock_get_last, mock_get_or_create):
    """Test /rus command when user has no attempted sentences"""
    # Setup mocks
    mock_get_or_create.return_value = None
    mock_get_last.return_value = None  # No sentences
    
    # Create mock message
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = User(id=12345, first_name="Test", is_bot=False, language_code="en")
    mock_message.answer = AsyncMock()
    
    # Create handler and test
    from src.state.learning_state import LearningState
    learning_state = LearningState()
    mock_bot = AsyncMock()
    handler = create_rus_command_handler(learning_state, mock_bot)
    await handler(mock_message)
    
    # Verify
    mock_get_or_create.assert_called_once()
    mock_get_last.assert_called_once_with(12345)
    mock_message.answer.assert_called_once()
    
    # Check the message content
    call_args = mock_message.answer.call_args
    message_text = call_args[0][0]
    assert "🔤 <b>Traduzione italiana-russo</b>" in message_text
    assert "Non hai ancora provato nessuna frase italiana." in message_text
    assert "Usa /start per iniziare a giocare" in message_text


@pytest.mark.asyncio
@patch('src.bot_commands.rus.get_or_create_user')
@patch('src.bot_commands.rus.get_last_attempted_sentence')
async def test_rus_command_user_creation(mock_get_last, mock_get_or_create):
    """Test that /rus command creates user if not exists"""
    # Setup mocks
    mock_get_or_create.return_value = None
    mock_get_last.return_value = None
    
    # Create mock message
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = User(id=12345, first_name="Test", is_bot=False, language_code="en")
    mock_message.answer = AsyncMock()
    
    # Create handler and test
    from src.state.learning_state import LearningState
    learning_state = LearningState()
    mock_bot = AsyncMock()
    handler = create_rus_command_handler(learning_state, mock_bot)
    await handler(mock_message)
    
    # Verify user creation is called
    mock_get_or_create.assert_called_once_with(mock_message.from_user)
