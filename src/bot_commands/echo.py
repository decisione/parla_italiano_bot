"""
Echo message handler for Parla Italiano Bot.

This module handles generic message responses and can be extended
for future message processing functionality.
"""

from aiogram.types import Message

import sys
import os

# Add the project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from src.database import get_or_create_user
except ImportError:
    # Fallback for Docker environment
    from database import get_or_create_user


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
        await message.answer(f"<blockquote>{message.text}</blockquote>\n\nPer ora niente chat interattiva, forse più avanti.", parse_mode="HTML")

    return echo_message_handler