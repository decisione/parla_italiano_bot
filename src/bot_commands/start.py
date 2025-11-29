"""
Start command handler for Parla Italiano Bot.

This module handles the /start command which initializes the user's
Italian language learning session and starts the first exercise.
"""

from aiogram.types import Message
from aiogram.filters import CommandStart

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_or_create_user


def create_start_command_handler(sentence_exercise):
    """
    Create a start command handler with dependency injection.
    
    Args:
        sentence_exercise: SentenceOrderingExercise instance
        
    Returns:
        Async function that handles the /start command
    """
    async def start_command_handler(message: Message) -> None:
        """
        Handle the /start command.
        
        Args:
            message: Telegram message object
        """
        user_id = message.from_user.id
        await get_or_create_user(message.from_user)
        await sentence_exercise.start_new_exercise(message, user_id)
    
    return start_command_handler