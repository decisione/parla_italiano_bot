"""
Shared utilities module for Parla Italiano Bot.

This module provides common utilities including validation, LLM integration,
and data processing functions used across different database modules.
"""

import logging
import random
import asyncio
import pydantic
from typing import List, Optional
from openai import OpenAI
import instructor
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock config for testing if config.ini doesn't exist
class MockValidationConfig:
    italian_characters: set = set('abcdefghiklmnopqrstuvzàèéìíîòóùú .,;:!?\'-')

class MockConfig:
    def __init__(self):
        self.validation = MockValidationConfig()

def get_validation_config():
    """Get validation configuration, with fallback for testing"""
    try:
        from config import get_validation_config as real_get_validation_config
        return real_get_validation_config()
    except FileNotFoundError:
        # Return mock config for testing when config.ini doesn't exist
        return MockConfig().validation

def get_llm_config():
    """Get LLM configuration, with fallback for testing"""
    try:
        from config import get_llm_config as real_get_llm_config
        return real_get_llm_config()
    except FileNotFoundError:
        # Return mock config for testing
        class MockLLMConfig:
            api_key = "test-key"
            api_url = "https://test.api"
            model_name = "test-model"
        return MockLLMConfig()


# Pydantic model for structured output
class SentenceList(pydantic.BaseModel):
    sentences: List[str]


def is_valid_italian_sentence(sentence: str) -> bool:
    """
    Validate that a sentence:
    1. Contains only Italian letters (including accented characters)
    2. Has between 3 and 10 words
    3. Does not contain duplicate words
    """
    validation_config = get_validation_config()
    
    # Check word count
    word_count = len(sentence.split())
    if word_count < 3 or word_count > 10:
        return False
    
    # Check for duplicate words
    words = sentence.lower().split()
    if len(words) != len(set(words)):
        return False
    
    # Check character set
    sentence_lower = sentence.lower()
    for char in sentence_lower:
        if char not in validation_config.italian_characters:
            return False
    
    return True


def clean_sentence(sentence: str) -> str:
    """Clean and normalize sentence"""
    # Remove extra whitespace and normalize
    return ' '.join(sentence.strip().split())


async def get_llm_client():
    """Get configured LLM client"""
    llm_config = get_llm_config()
    
    # Check if API key is available
    if not llm_config.api_key:
        raise ValueError("LLM_API_KEY not found in environment variables")
    
    return instructor.patch(OpenAI(base_url=llm_config.api_url, api_key=llm_config.api_key))


async def execute_with_retry(func, max_retries: int = 5, base_delay: int = 1):
    """
    Execute a function with retry logic for handling transient errors.
    
    Args:
        func: Async function to execute
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
    
    Returns:
        Result of the executed function
    
    Raises:
        Exception: If all retry attempts fail
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            # Check if it's a rate limit error (429)
            if hasattr(e, 'status_code') and e.status_code == 429:
                if attempt < max_retries - 1:  # Don't wait on the last attempt
                    # Wait a random amount of time between base_delay and base_delay * 2^attempt
                    wait_time = random.uniform(base_delay, base_delay * (2 ** attempt))
                    logging.info(f"Rate limited. Waiting {wait_time:.2f} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logging.error(f"Rate limit exceeded after {max_retries} attempts")
                    raise
            else:
                if attempt < max_retries - 1:  # Don't wait on the last attempt
                    # Wait before retrying for other types of errors
                    wait_time = random.uniform(base_delay, base_delay * (2 ** attempt))
                    logging.info(f"Waiting {wait_time:.2f} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logging.error(f"Failed after {max_retries} attempts: {e}")
                    raise