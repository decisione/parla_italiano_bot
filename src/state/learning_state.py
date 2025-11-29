"""
User learning state management for Parla Italiano Bot.

This module handles the management of user learning state during sentence ordering exercises.
It replaces the global user_game_state dictionary with a proper class-based approach.
"""

from typing import Dict, List, Optional, Any


class LearningState:
    """
    Manages user learning state for sentence ordering exercises.
    """
    
    def __init__(self):
        """Initialize the learning state storage."""
        self._user_states: Dict[int, Dict[str, Any]] = {}
    
    def get_user_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the learning state for a specific user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary containing user's learning state or None if not found
        """
        return self._user_states.get(user_id)
    
    def set_user_state(self, user_id: int, state: Dict[str, Any]) -> None:
        """
        Set the learning state for a specific user.
        
        Args:
            user_id: Telegram user ID
            state: Dictionary containing user's learning state
        """
        self._user_states[user_id] = state
    
    def clear_user_state(self, user_id: int) -> None:
        """
        Clear the learning state for a specific user.
        
        Args:
            user_id: Telegram user ID
        """
        self._user_states.pop(user_id, None)
    
    def has_user_state(self, user_id: int) -> bool:
        """
        Check if a user has an active learning state.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user has an active state, False otherwise
        """
        return user_id in self._user_states
    
    def get_selected_words(self, user_id: int) -> List[str]:
        """
        Get the list of selected words for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of selected words, empty list if no state exists
        """
        state = self.get_user_state(user_id)
        if state and 'selected_words' in state:
            return state['selected_words']
        return []
    
    def add_selected_word(self, user_id: int, word: str) -> None:
        """
        Add a word to the user's selected words list.
        
        Args:
            user_id: Telegram user ID
            word: Word to add to selection
        """
        state = self.get_user_state(user_id)
        if state and 'selected_words' in state:
            state['selected_words'].append(word)
    
    def get_remaining_words(self, user_id: int) -> List[str]:
        """
        Get the list of remaining words that haven't been selected yet.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of remaining words
        """
        state = self.get_user_state(user_id)
        if not state:
            return []
        
        selected_words = state.get('selected_words', [])
        shuffled_words = state.get('shuffled_words', [])
        
        return [word for word in shuffled_words if word not in selected_words]
    
    def is_exercise_complete(self, user_id: int) -> bool:
        """
        Check if the user has completed the current exercise.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if exercise is complete, False otherwise
        """
        state = self.get_user_state(user_id)
        if not state:
            return False
        
        selected_words = state.get('selected_words', [])
        current_sentence_words = state.get('current_sentence_words', [])
        
        return len(selected_words) == len(current_sentence_words)
    
    def get_original_sentence(self, user_id: int) -> Optional[str]:
        """
        Get the original sentence for the user's current exercise.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Original sentence text or None if no state exists
        """
        state = self.get_user_state(user_id)
        return state.get('original_sentence') if state else None
    
    def get_current_sentence_words(self, user_id: int) -> List[str]:
        """
        Get the list of words in the current sentence.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of words in the current sentence, empty list if no state exists
        """
        state = self.get_user_state(user_id)
        if state and 'current_sentence_words' in state:
            return state['current_sentence_words']
        return []
    
    def get_sentence_id(self, user_id: int) -> Optional[int]:
        """
        Get the sentence ID for the user's current exercise.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Sentence ID or None if no state exists
        """
        state = self.get_user_state(user_id)
        return state.get('sentence_id') if state else None
    
    def get_all_user_ids(self) -> List[int]:
        """
        Get all user IDs that have active learning states.
        
        Returns:
            List of user IDs
        """
        return list(self._user_states.keys())
    
    def cleanup_expired_states(self) -> None:
        """
        Clean up any expired or invalid states.
        Currently a placeholder for future implementation.
        """
        # Future implementation could add expiration logic
        pass