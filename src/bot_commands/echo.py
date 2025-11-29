"""
Echo message handler for Parla Italiano Bot.

This module handles generic message responses and can be extended
for future message processing functionality.
"""

from aiogram.types import Message

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_or_create_user


def create_echo_handler():
    """
    Create an echo message handler.
    
    Returns:
        Async function that handles generic messages
    """
    async def echo_message_handler(message: Message) -> None:
        """
        Handle generic text messages with an echo response.
        
        Args:
            message: Telegram message object
        """
        await get_or_create_user(message.from_user)
        await message.answer(f"You said: {message.text}")
    
    return echo_message_handler