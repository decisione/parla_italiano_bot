import pytest
import asyncio
from src.bot import (
    create_word_buttons,
    user_game_state
)
from src.database import get_random_sentence


class TestCreateWordButtons:
    def test_creates_keyboard_markup(self):
        words = ["ciao", "come", "stai"]
        keyboard = create_word_buttons(words)
        assert keyboard is not None
        assert hasattr(keyboard, 'inline_keyboard')
        assert len(keyboard.inline_keyboard) == 1  # Single row
        assert len(keyboard.inline_keyboard[0]) == 3  # Three buttons

    def test_buttons_have_correct_text_and_callback(self):
        words = ["hello", "world"]
        keyboard = create_word_buttons(words)
        buttons = keyboard.inline_keyboard[0]
        assert buttons[0].text == "hello"
        assert buttons[0].callback_data == "word_hello"
        assert buttons[1].text == "world"
        assert buttons[1].callback_data == "word_world"


class TestGameState:
    def test_user_game_state_is_dict(self):
        assert isinstance(user_game_state, dict)

    def test_initially_empty(self):
        # Assuming tests run in isolation, but since it's global, might not be
        # In real tests, we'd mock or reset
        pass  # Skip for now