"""
Russian translation command handler for Parla Italiano Bot.

This module handles the /rus command which displays the Russian translation
of the last attempted Italian sentence for the user.
"""

from aiogram.types import Message
from aiogram.filters import Command

import sys
import os

# Add the project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from src.database import get_or_create_user, get_last_attempted_sentence
except ImportError:
    # Fallback for Docker environment
    from database import get_or_create_user, get_last_attempted_sentence


def create_rus_command_handler():
    """
    Create a Russian translation command handler.
    
    Returns:
        Async function that handles the /rus command
    """
    async def rus_command_handler(message: Message) -> None:
        """
        Handle the /rus command.
        
        Args:
            message: Telegram message object
        """
        user_id = message.from_user.id
        await get_or_create_user(message.from_user)
        
        # Get the last attempted sentence for this user
        last_sentence = await get_last_attempted_sentence(user_id)
        
        if last_sentence:
            italian_sentence = last_sentence['italian']
            russian_translation = last_sentence['russian']
            
            if russian_translation:
                # Display both Italian and Russian sentences
                translation_text = f"""🔤 <b>Traduzione italiana-russo</b>:

🇮🇹 <i>{italian_sentence}</i>
🇷🇺 <b>{russian_translation}</b>"""
            else:
                # No Russian translation available yet
                translation_text = f"""🔤 <b>Traduzione italiana-russo</b>:

🇮🇹 <i>{italian_sentence}</i>
🇷🇺 <b>Traduzione non disponibile ancora</b>

Continua a giocare per sbloccare le traduzioni!"""
        else:
            # No sentences attempted yet
            translation_text = """🔤 <b>Traduzione italiana-russo</b>:

Non hai ancora provato nessuna frase italiana.
Usa /start per iniziare a giocare e poi potrai vedere le traduzioni!"""
        
        await message.answer(translation_text, parse_mode="HTML")
    
    return rus_command_handler