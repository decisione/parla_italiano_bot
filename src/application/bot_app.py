"""
Main application orchestrator for Parla Italiano Bot.

This module provides the main application class that orchestrates all
components including command handlers, exercise modules, state management,
and the Telegram bot framework integration.
"""

import logging
import os
import asyncio
from typing import Optional
import sys

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message

# Add the project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from config import get_bot_config, get_logging_config
    from database import get_schema_migrations, get_table_counts
    from state.learning_state import LearningState
    from exercises.sentence_ordering import SentenceOrderingExercise
    from bot_commands import create_start_command_handler, create_echo_handler, create_help_command_handler, create_stats_command_handler
except ImportError:
    # Fallback for Docker environment
    from src.config import get_bot_config, get_logging_config
    from src.database import get_schema_migrations, get_table_counts
    from src.state.learning_state import LearningState
    from src.exercises.sentence_ordering import SentenceOrderingExercise
    from src.bot_commands import create_start_command_handler, create_echo_handler, create_help_command_handler


class ParlaItalianoBot:
    """
    Main application class for Parla Italiano Bot.
    
    Orchestrates all components including bot framework, command handlers,
    exercise modules, and state management.
    """
    
    def __init__(self):
        """Initialize the bot application with all components."""
        # Initialize configuration
        self.bot_config = get_bot_config()
        
        # Initialize bot framework components
        self.bot = Bot(token=self.bot_config.token)
        self.dp = Dispatcher()
        self.router = Router()
        
        # Initialize application components
        self.learning_state = LearningState()
        self.sentence_exercise = SentenceOrderingExercise(self.learning_state)
        
        # Initialize command handlers
        self._setup_command_handlers()
        self._setup_callback_handlers()
        self._setup_message_handlers()
        
        # Attach router to dispatcher
        self.dp.include_router(self.router)
    
    def _setup_command_handlers(self) -> None:
        """Setup command handlers."""
        # Create and register /start command handler
        start_handler = create_start_command_handler(self.sentence_exercise)
        self.router.message(CommandStart())(start_handler)
        
        # Create and register /help command handler
        help_handler = create_help_command_handler()
        self.router.message(Command("help"))(help_handler)
        
        # Create and register /stats command handler
        stats_handler = create_stats_command_handler()
        self.router.message(Command("stats"))(stats_handler)
    
    def _setup_callback_handlers(self) -> None:
        """Setup callback query handlers."""
        @self.router.callback_query(F.data.startswith("word_"))
        async def handle_word_selection(callback: CallbackQuery) -> None:
            """Handle word button selections in sentence ordering exercise."""
            await self.sentence_exercise.handle_word_selection(callback)
    
    def _setup_message_handlers(self) -> None:
        """Setup message handlers."""
        # Create and register echo handler
        echo_handler = create_echo_handler()
        self.router.message()(echo_handler)
    
    async def _setup_logging(self) -> None:
        """Setup application logging."""
        logging_config = get_logging_config()
        os.makedirs(logging_config.log_dir, exist_ok=True)
        log_file = os.path.join(logging_config.log_dir, 'bot.log')
        
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    async def _log_initialization_info(self) -> None:
        """Log application initialization information."""
        logging.info("-"*80)
        logging.info("Bot is starting...")
        logging.info("Connecting to database for init logging...")
        
        # Log schema migrations
        migrations = await get_schema_migrations()
        for migration in migrations:
            logging.info(f"Schema migration: {migration}")
        
        # Log table counts
        counts = await get_table_counts()
        for table, count in counts.items():
            logging.info(f"Table {table}: {count} rows")
        
        logging.info("Starting polling...")
    
    async def start(self) -> None:
        """
        Start the bot application.
        
        This method sets up logging, logs initialization information,
        and starts the bot polling.
        """
        await self._setup_logging()
        await self._log_initialization_info()
        await self.dp.start_polling(self.bot)
    
    def get_dispatcher(self) -> Dispatcher:
        """
        Get the bot dispatcher for testing or external use.
        
        Returns:
            Dispatcher instance
        """
        return self.dp
    
    def get_bot(self) -> Bot:
        """
        Get the bot instance for testing or external use.
        
        Returns:
            Bot instance
        """
        return self.bot


async def main() -> None:
    """
    Main entry point for the bot application.
    
    Creates the application instance and starts the bot.
    """
    app = ParlaItalianoBot()
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())