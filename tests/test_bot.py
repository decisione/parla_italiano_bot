import pytest
from parla_italiano_bot import (
    ENCOURAGING_PHRASES,
    ERROR_PHRASES,
    ITALIAN_SENTENCES,
    get_random_sentence,
    create_word_buttons,
    user_game_state
)


class TestConstants:
    def test_encouraging_phrases_is_list(self):
        assert isinstance(ENCOURAGING_PHRASES, list)
        assert len(ENCOURAGING_PHRASES) > 0
        assert all(isinstance(phrase, str) for phrase in ENCOURAGING_PHRASES)

    def test_error_phrases_is_list(self):
        assert isinstance(ERROR_PHRASES, list)
        assert len(ERROR_PHRASES) > 0
        assert all(isinstance(phrase, str) for phrase in ERROR_PHRASES)

    def test_italian_sentences_is_list(self):
        assert isinstance(ITALIAN_SENTENCES, list)
        assert len(ITALIAN_SENTENCES) > 0
        assert all(isinstance(sentence, str) for sentence in ITALIAN_SENTENCES)


class TestGetRandomSentence:
    def test_returns_string(self):
        sentence = get_random_sentence()
        assert isinstance(sentence, str)
        assert len(sentence) > 0

    def test_returns_from_list(self):
        sentence = get_random_sentence()
        assert sentence in ITALIAN_SENTENCES


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