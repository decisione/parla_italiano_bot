"""
Stats command handler for Parla Italiano Bot.

This module handles the /stats command which provides statistics
about the bot usage and user performance.
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
    from src.database import get_or_create_user, get_stats_data
except ImportError:
    # Fallback for Docker environment
    from database import get_or_create_user, get_stats_data


def create_stats_command_handler():
    """
    Create a stats command handler.
    
    Returns:
        Async function that handles the /stats command
    """
    async def stats_command_handler(message: Message) -> None:
        """
        Handle the /stats command.
        
        Args:
            message: Telegram message object
        """
        user_id = message.from_user.id
        await get_or_create_user(message.from_user)
        
        # Get statistics data
        stats = await get_stats_data(user_id)
        
        # Format statistics in Italian
        stats_text = f"""
<u>Statistiche del Bot:</u>
- Utenti totali: <b>{stats['total_users']}</b>
- Frasi totali: <b>{stats['total_sentences']}</b> (aggiunto automaticamente se necessario)

<u>Statistiche di tutti i tempi:</u>
- Tentativi globali: <b>{stats['total_attempts']}</b>
- Successo globale: <b>{stats['global_success_rate']:.1f}%</b>, personale: <b>{stats['user_success_rate']:.1f}%</b>

<u>Statistiche di oggi:</u>
- Tentativi globali: <b>{stats['today_global_attempts']}</b>, i tuoi tentativi: <b>{stats['today_user_attempts']}</b>
- Successo globale: <b>{stats['today_global_success_rate']:.1f}%</b>, personale: <b>{stats['today_user_success_rate']:.1f}%</b>"""
        
        await message.answer(stats_text, parse_mode="HTML")
    
    return stats_command_handler