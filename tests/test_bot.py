import pytest
import asyncio
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.exercises.sentence_ordering import SentenceOrderingExercise
from src.state.learning_state import LearningState
from src.database import get_random_sentence


class TestCreateWordButtons:
    def test_creates_keyboard_markup(self):
        # Create a mock learning state for testing
        learning_state = LearningState()
        sentence_exercise = SentenceOrderingExercise(learning_state)
        
        words = ["ciao", "come", "stai"]
        keyboard = sentence_exercise.create_word_buttons(words)
        assert keyboard is not None
        assert hasattr(keyboard, 'inline_keyboard')
        assert len(keyboard.inline_keyboard) == 1  # Single row
        assert len(keyboard.inline_keyboard[0]) == 3  # Three buttons

    def test_buttons_have_correct_text_and_callback(self):
        # Create a mock learning state for testing
        learning_state = LearningState()
        sentence_exercise = SentenceOrderingExercise(learning_state)
        
        words = ["hello", "world"]
        keyboard = sentence_exercise.create_word_buttons(words)
        buttons = keyboard.inline_keyboard[0]
        assert buttons[0].text == "hello"
        assert buttons[0].callback_data == "word_hello"
        assert buttons[1].text == "world"
        assert buttons[1].callback_data == "word_world"


class TestLearningState:
    def test_learning_state_is_class(self):
        learning_state = LearningState()
        assert isinstance(learning_state, LearningState)

    def test_initially_empty(self):
        learning_state = LearningState()
        # Learning state should start empty
        assert len(learning_state.get_all_user_ids()) == 0

    def test_user_state_management(self):
        learning_state = LearningState()
        user_id = 123
        
        # Initially no state
        assert not learning_state.has_user_state(user_id)
        assert learning_state.get_user_state(user_id) is None
        
        # Set state
        test_state = {'test': 'data'}
        learning_state.set_user_state(user_id, test_state)
        
        # Check state
        assert learning_state.has_user_state(user_id)
        assert learning_state.get_user_state(user_id) == test_state
        
        # Clear state
        learning_state.clear_user_state(user_id)
        assert not learning_state.has_user_state(user_id)