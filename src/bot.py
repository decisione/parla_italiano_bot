"""
Entry point for Parla Italiano Bot.

This is the main entry point that initializes and starts the bot application.
The actual application logic is modularized in the src/application/ directory.
"""

import asyncio
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application.bot_app import main as app_main


if __name__ == "__main__":
    asyncio.run(app_main())