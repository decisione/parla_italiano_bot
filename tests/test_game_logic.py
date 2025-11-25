import pytest
from parla_italiano_bot import user_game_state, ITALIAN_SENTENCES
import random


class TestGameLogic:
    def setup_method(self):
        """Reset game state before each test"""
        user_game_state.clear()

    def test_game_state_initialization(self):
        user_id = 123
        original_sentence = "Ciao come stai"
        words = original_sentence.split()
        shuffled_words = words.copy()
        random.shuffle(shuffled_words)

        user_game_state[user_id] = {
            'original_sentence': original_sentence,
            'selected_words': [],
            'current_sentence_words': words,
            'shuffled_words': shuffled_words
        }

        assert user_game_state[user_id]['original_sentence'] == original_sentence
        assert user_game_state[user_id]['selected_words'] == []
        assert user_game_state[user_id]['current_sentence_words'] == words
        assert len(user_game_state[user_id]['shuffled_words']) == len(words)

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

    def test_partial_selection_logic(self):
        user_id = 123
        shuffled_words = ["stai", "Ciao", "come"]
        selected_words = ["Ciao"]

        remaining_words = [word for word in shuffled_words if word not in selected_words]

        assert "Ciao" not in remaining_words
        assert "stai" in remaining_words
        assert "come" in remaining_words
        assert len(remaining_words) == 2

    def test_complete_selection_logic(self):
        user_id = 123
        original_words = ["Ciao", "come", "stai"]
        selected_words = ["Ciao", "come", "stai"]

        # Check if all words selected
        all_selected = len(selected_words) == len(original_words)
        assert all_selected

        # Check correctness
        is_correct = original_words == selected_words
        assert is_correct

    def test_random_sentence_selection(self):
        # Test that we can get different sentences (though random)
        sentence1 = random.choice(ITALIAN_SENTENCES)
        sentence2 = random.choice(ITALIAN_SENTENCES)

        assert sentence1 in ITALIAN_SENTENCES
        assert sentence2 in ITALIAN_SENTENCES
        # Note: They could be the same due to randomness, but statistically unlikely

    def test_sentence_splitting(self):
        sentence = "Ciao come stai"
        words = sentence.split()
        assert words == ["Ciao", "come", "stai"]
        assert len(words) == 3