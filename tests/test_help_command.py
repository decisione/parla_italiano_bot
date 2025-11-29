import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot_commands.help import create_help_command_handler


class TestHelpCommand:
    """Test suite for the help command handler."""
    
    @pytest.mark.asyncio
    async def test_help_command_handler(self):
        """Test that the help command handler returns the correct help text."""
        # Mock the database function
        with pytest.MonkeyPatch().context() as mp:
            mock_get_or_create_user = AsyncMock()
            mp.setattr("src.bot_commands.help.get_or_create_user", mock_get_or_create_user)
            
            # Create a mock message object
            mock_message = AsyncMock()
            mock_message.from_user = MagicMock()
            mock_message.from_user.id = 12345
            
            # Create the help command handler
            help_handler = create_help_command_handler()
            
            # Call the handler
            await help_handler(mock_message)
            
            # Verify that get_or_create_user was called with the correct user
            mock_get_or_create_user.assert_called_once_with(mock_message.from_user)
            
            # Verify that answer was called with the expected help text
            mock_message.answer.assert_called_once()
            help_text = mock_message.answer.call_args[0][0]
            
            # Check that the help text contains the expected content
            assert "Buongiorno!" in help_text
            assert "Questo bot ti aiuta a imparare l'italiano" in help_text
            assert "/start" in help_text
            assert "parole mescolate casualmente" in help_text
            assert "In bocca al lupo!" in help_text
