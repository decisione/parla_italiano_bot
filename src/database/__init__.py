"""
Database package for Parla Italiano Bot.

This package provides modular database operations including user management,
sentence handling, and shared utilities for the Italian learning bot.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all functions from submodules to maintain backward compatibility
from .connection import get_schema_migrations, get_table_counts, get_stats_data
from .users import get_or_create_user
from .sentences import (
    get_random_sentence,
    store_sentence_result,
    get_random_encouraging_phrase,
    get_random_error_phrase
)

# Re-export the SentenceList model for backward compatibility
from .base import SentenceList

# Import asyncpg for backward compatibility with existing tests
import asyncpg

__all__ = [
    # Connection functions
    'get_schema_migrations',
    'get_table_counts',
    'get_stats_data',
    
    # User functions
    'get_or_create_user',
    
    # Sentence functions
    'get_random_sentence',
    'store_sentence_result',
    'get_random_encouraging_phrase',
    'get_random_error_phrase',
    
    # Models
    'SentenceList',
    
    # For backward compatibility
    'asyncpg'
]