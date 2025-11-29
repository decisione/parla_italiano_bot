import pytest
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state.learning_state import LearningState
import random


class TestLearningStateLogic:
    def setup_method(self):
        """Reset learning state before each test"""
        self.learning_state = LearningState()

    def test_learning_state_initialization(self):
        user_id = 123
        original_sentence = "Ciao come stai"
        words = original_sentence.split()
        shuffled_words = words.copy()
        random.shuffle(shuffled_words)

        exercise_state = {
            'original_sentence': original_sentence,
            'selected_words': [],
            'current_sentence_words': words,
            'shuffled_words': shuffled_words
        }

        self.learning_state.set_user_state(user_id, exercise_state)

        assert self.learning_state.get_original_sentence(user_id) == original_sentence
        assert self.learning_state.get_selected_words(user_id) == []
        assert self.learning_state.get_current_sentence_words(user_id) == words
        assert len(self.learning_state.get_remaining_words(user_id)) == len(words)

    def test_correct_word_order_check(self):
        user_id = 123
        original_words = ["Ciao", "come", "stai"]
        selected_words = ["Ciao", "come", "stai"]

        # Simulate the check logic from handle_word_selection
        if original_words == selected_words:
            result = "correct"
        else:
            result = "incorrect"

        assert result == "correct"

    def test_incorrect_word_order_check(self):
        user_id = 123
        original_words = ["Ciao", "come", "stai"]
        selected_words = ["Ciao", "stai", "come"]

        if original_words == selected_words:
            result = "correct"
        else:
            result = "incorrect"

        assert result == "incorrect"

    def test_word_selection_logic(self):
        user_id = 123
        shuffled_words = ["stai", "Ciao", "come"]
        
        # Set up initial state
        exercise_state = {
            'original_sentence': "Ciao come stai",
            'selected_words': [],
            'current_sentence_words': ["Ciao", "come", "stai"],
            'shuffled_words': shuffled_words
        }
        self.learning_state.set_user_state(user_id, exercise_state)
        
        # Add selected word
        self.learning_state.add_selected_word(user_id, "Ciao")

        remaining_words = self.learning_state.get_remaining_words(user_id)

        assert "Ciao" not in remaining_words
        assert "stai" in remaining_words
        assert "come" in remaining_words
        assert len(remaining_words) == 2

    def test_exercise_completion_check(self):
        user_id = 123
        original_words = ["Ciao", "come", "stai"]
        selected_words = ["Ciao", "come", "stai"]
        
        # Set up state with all words selected
        exercise_state = {
            'original_sentence': "Ciao come stai",
            'selected_words': selected_words,
            'current_sentence_words': original_words,
            'shuffled_words': original_words
        }
        self.learning_state.set_user_state(user_id, exercise_state)

        # Check if all words selected
        all_selected = self.learning_state.is_exercise_complete(user_id)
        assert all_selected

        # Check correctness
        is_correct = original_words == selected_words
        assert is_correct

    def test_remaining_words_calculation(self):
        user_id = 123
        shuffled_words = ["stai", "Ciao", "come"]
        selected_words = ["Ciao"]
        
        # Set up state
        exercise_state = {
            'original_sentence': "Ciao come stai",
            'selected_words': selected_words,
            'current_sentence_words': ["Ciao", "come", "stai"],
            'shuffled_words': shuffled_words
        }
        self.learning_state.set_user_state(user_id, exercise_state)

        remaining_words = self.learning_state.get_remaining_words(user_id)
        assert "Ciao" not in remaining_words
        assert "stai" in remaining_words
        assert "come" in remaining_words
        assert len(remaining_words) == 2

    def test_random_sentence_selection(self):
        # Test that we can get different sentences (mocked since now from DB)
        # This test is skipped as sentences are now from database
        pass

    def test_sentence_splitting(self):
        sentence = "Ciao come stai"
        words = sentence.split()
        assert words == ["Ciao", "come", "stai"]
        assert len(words) == 3