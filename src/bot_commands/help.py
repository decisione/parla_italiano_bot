"""
Help command handler for Parla Italiano Bot.

This module handles the /help command which provides information
about the bot's functionality and how to use it.
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
    from src.database import get_or_create_user
except ImportError:
    # Fallback for Docker environment
    from database import get_or_create_user


def create_help_command_handler():
    """
    Create a help command handler.
    
    Returns:
        Async function that handles the /help command
    """
    async def help_command_handler(message: Message) -> None:
        """
        Handle the /help command.
        
        Args:
            message: Telegram message object
        """
        user_id = message.from_user.id
        await get_or_create_user(message.from_user)
        
        help_text = """Buongiorno!

Questo bot ti aiuta a imparare l'italiano. Per ora ha un solo esercizio, che può essere avviato con il comando /start.

Questo esercizio ti presenterà una frase in italiano con le parole mescolate casualmente. Il tuo compito è metterle nell'ordine corretto. Ci sono frasi illimitate per te. Non vedrai mai le frasi che hai risolto correttamente.

Altri esercizi in arrivo!

Puoi anche usare il comando /rus per ottenere la traduzione in russo del tuo ultimo tentativo.

Inoltre, puoi vedere alcune statistiche con il comando /stats.

In bocca al lupo!"""
        
        await message.answer(help_text)
    
    return help_command_handler