"""
Test for sentence replenishment fix to ensure it doesn't block the event loop.

This test verifies that the sentence_replenishment function runs in the background
without blocking the main bot operations.
"""

import asyncio
import pytest
import time
from unittest.mock import patch, MagicMock
from src.database.sentences import sentence_replenishment


@pytest.mark.asyncio
async def test_sentence_replenishment_does_not_block():
    """
    Test that sentence_replenishment runs in the background without blocking.
    
    This test verifies that:
    1. The function can be started as a background task
    2. The main event loop continues to run while replenishment is happening
    3. The function completes without blocking other operations
    """
    # Track if the main loop was blocked
    main_loop_blocked = False
    start_time = time.time()
    
    async def monitor_main_loop():
        """Monitor if the main event loop gets blocked"""
        nonlocal main_loop_blocked
        await asyncio.sleep(0.1)  # Give some time for potential blocking
        if time.time() - start_time > 0.5:  # If more than 500ms passed, something is blocking
            main_loop_blocked = True
    
    # Mock the LLM API call to simulate a slow response
    with patch('src.database.sentences.execute_with_retry_sync') as mock_retry:
        # Mock the generate_sentences function to simulate a slow API call
        def slow_generate_sentences():
            time.sleep(0.3)  # Simulate 300ms API call
            return ["Ciao come stai", "Buongiorno", "Come ti chiami"]
        
        mock_retry.return_value = slow_generate_sentences()
        
        # Start the replenishment as a background task
        replenishment_task = asyncio.create_task(sentence_replenishment(12345))
        
        # Start monitoring the main loop
        monitor_task = asyncio.create_task(monitor_main_loop())
        
        # Wait for both tasks to complete
        await asyncio.gather(replenishment_task, monitor_task)
        
        # Assert that the main loop was not blocked
        assert not main_loop_blocked, "Main event loop was blocked during sentence replenishment"
        
        # Verify that the function completed in reasonable time
        total_time = time.time() - start_time
        assert total_time < 1.0, f"Function took too long: {total_time:.2f} seconds"


@pytest.mark.asyncio
async def test_sentence_replenishment_with_mock_llm():
    """
    Test sentence_replenishment with mocked LLM to ensure it works correctly.
    """
    with patch('src.database.sentences.get_llm_config') as mock_llm_config, \
         patch('src.database.sentences.execute_with_retry_sync') as mock_retry, \
         patch('src.database.sentences.asyncpg.connect') as mock_connect:
        
        # Setup mocks
        mock_llm_config.return_value.api_key = "test-key"
        
        def mock_generate_sentences():
            return ["Ciao come stai", "Buongiorno", "Come ti chiami"]
        
        mock_retry.return_value = mock_generate_sentences()
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchrow.return_value = None  # No duplicates
        mock_conn.__aenter__.return_value = mock_conn
        mock_conn.__aexit__.return_value = None
        mock_connect.return_value = mock_conn
        
        # Run the function
        start_time = time.time()
        await sentence_replenishment(12345)
        duration = time.time() - start_time
        
        # Verify it completed quickly (since we're using mocks)
        assert duration < 1.0, f"Function took too long with mocks: {duration:.2f} seconds"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])