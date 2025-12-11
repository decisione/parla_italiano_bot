"""
Sentence ordering exercise module for Parla Italiano Bot.

This module handles the sentence word ordering exercise where users
must arrange scrambled Italian words to form a correct sentence.
"""

import random
from typing import List, Tuple, Optional
from aiogram import types
from aiogram.types import CallbackQuery, Message

import sys
import os

# Add the project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from src.database import (
        get_random_sentence,
        get_random_encouraging_phrase,
        get_random_error_phrase,
        store_sentence_result,
        get_or_create_user
    )
except ImportError:
    # Fallback for Docker environment
    from database import (
        get_random_sentence,
        get_random_encouraging_phrase,
        get_random_error_phrase,
        store_sentence_result,
        get_or_create_user
    )


class SentenceOrderingExercise:
    """
    Handles sentence word ordering exercises for Italian language learning.
    """
    
    def __init__(self, learning_state):
        """
        Initialize the sentence ordering exercise.
        
        Args:
            learning_state: LearningState instance for managing user progress
        """
        self.learning_state = learning_state
    
    def create_word_buttons(self, shuffled_words: List[str]) -> types.InlineKeyboardMarkup:
        """
        Create inline keyboard buttons for each word in the shuffled order.
        
        Args:
            shuffled_words: List of words in shuffled order
            
        Returns:
            InlineKeyboardMarkup with word buttons arranged in rows
        """
        keyboard_rows = []
        current_row = []
        
        for word in shuffled_words:
            current_row.append(types.InlineKeyboardButton(
                text=word, 
                callback_data=f"word_{word}"
            ))
            
            # Start a new row after every 4 buttons
            if len(current_row) == 4:
                keyboard_rows.append(current_row)
                current_row = []
        
        # Add any remaining buttons in the last row
        if current_row:
            keyboard_rows.append(current_row)
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
        return keyboard
    
    async def start_new_exercise(self, message_or_callback: Message | CallbackQuery, user_id: int) -> None:
        """
        Start a new sentence ordering exercise for the user.
        
        Args:
            message_or_callback: Telegram message or callback query
            user_id: Telegram user ID
        """
        # Get random sentence and store original order
        sentence_id, original_sentence = await get_random_sentence(user_id)
        words = original_sentence.split()
        random.shuffle(words)  # Shuffle once and store this order
        
        # Store exercise state
        exercise_state = {
            'sentence_id': sentence_id,
            'original_sentence': original_sentence,
            'selected_words': [],
            'current_sentence_words': original_sentence.split(),
            'shuffled_words': words  # Store the shuffled order
        }
        
        self.learning_state.set_user_state(user_id, exercise_state)
        
        # Create buttons with words in the shuffled order
        keyboard = self.create_word_buttons(words)
        
        # Send exercise prompt
        message_text = "Disponi queste parole per formare la frase italiana corretta:"
        
        if hasattr(message_or_callback, 'message'):
            # It's a callback query
            await message_or_callback.answer()
            sent_message = await message_or_callback.message.edit_text(
                message_text,
                reply_markup=keyboard
            )
            # Store the message ID for the callback case
            self.learning_state.set_message_id(user_id, sent_message.message_id)
        else:
            # It's a message
            sent_message = await message_or_callback.answer(
                message_text,
                reply_markup=keyboard
            )
            # Store the message ID for the message case
            self.learning_state.set_message_id(user_id, sent_message.message_id)
    
    async def handle_word_selection(self, callback: CallbackQuery) -> None:
        """
        Handle user selection of a word button.
        
        Args:
            callback: Telegram callback query from word button
        """
        user_id = callback.from_user.id
        await get_or_create_user(callback.from_user)
        selected_word = callback.data.replace("word_", "")
        
        # Check if user has an active exercise
        if not self.learning_state.has_user_state(user_id):
            await callback.answer("Per favore, avvia prima l'esercizio con /start")
            return
        
        # Add selected word to user's selection
        self.learning_state.add_selected_word(user_id, selected_word)
        
        # Check if exercise is complete
        if self.learning_state.is_exercise_complete(user_id):
            await self._handle_exercise_completion(callback, user_id)
        else:
            await self._update_exercise_progress(callback, user_id)
    
    async def _handle_exercise_completion(self, callback: CallbackQuery, user_id: int) -> None:
        """
        Handle completion of a sentence ordering exercise.
        
        Args:
            callback: Telegram callback query
            user_id: Telegram user ID
        """
        original_words = self.learning_state.get_current_sentence_words(user_id)
        selected_order = self.learning_state.get_selected_words(user_id)
        
        if original_words == selected_order:
            # Correct answer
            await self._handle_correct_answer(callback, user_id, original_words)
        else:
            # Incorrect answer
            await self._handle_incorrect_answer(callback, user_id, original_words, selected_order)
        
        # Start next exercise after a short delay
        import asyncio
        await asyncio.sleep(1)
        await self.start_new_exercise(callback.message, user_id)
    
    async def _handle_correct_answer(self, callback: CallbackQuery, user_id: int, original_words: List[str]) -> None:
        """
        Handle correct answer for sentence ordering exercise.
        
        Args:
            callback: Telegram callback query
            user_id: Telegram user ID
            original_words: List of words in correct order
        """
        # Select a random encouraging phrase
        phrase = await get_random_encouraging_phrase()
        emojis = ["🎉", "✅", "💣", "💥", "🥳", "🎆", "🎇", "🤩", "😎", "🥳", "💪", "👍", "🎈", "🎯", "🥇", "🏅", "🎖️", "🏆"]
        emoji = random.choice(emojis)
        
        await callback.message.edit_text(
            f"{emoji} {phrase} {emoji}\n\n<blockquote>{' '.join(original_words)}</blockquote>\n",
            parse_mode="HTML"
        )
        await callback.answer("Corretto!")
        
        # Store the result
        sentence_id = self.learning_state.get_sentence_id(user_id)
        if sentence_id is not None:
            await store_sentence_result(user_id, sentence_id, True)
    
    async def _handle_incorrect_answer(self, callback: CallbackQuery, user_id: int, original_words: List[str], selected_order: List[str]) -> None:
        """
        Handle incorrect answer for sentence ordering exercise.
        
        Args:
            callback: Telegram callback query
            user_id: Telegram user ID
            original_words: List of words in correct order
            selected_order: List of words in user's selected order
        """
        # Select a random error phrase
        phrase = await get_random_error_phrase()
        emojis = ["❌", "✖️", "⚠️", "⁉️", "🆘", "🚫", "📛", "🛑", "⛔", "🌩️", "🪫", "🩻", "🧱", "🤚", "👎", "😞", "😪", "😣", "🥲"]
        emoji = random.choice(emojis)
        
        await callback.message.edit_text(
            f"{emoji} {phrase}\n\nLa tua risposta: <blockquote>{' '.join(selected_order)}</blockquote>\nOrdine corretto: <blockquote>{' '.join(original_words)}</blockquote>\n",
            parse_mode="HTML"
        )
        await callback.answer("Ordine sbagliato!")
        
        # Store the result
        sentence_id = self.learning_state.get_sentence_id(user_id)
        if sentence_id is not None:
            await store_sentence_result(user_id, sentence_id, False)
    
    async def _update_exercise_progress(self, callback: CallbackQuery, user_id: int) -> None:
        """
        Update the exercise interface with current progress.
        
        Args:
            callback: Telegram callback query
            user_id: Telegram user ID
        """
        # Create keyboard with remaining buttons
        remaining_words = self.learning_state.get_remaining_words(user_id)
        keyboard = self.create_word_buttons(remaining_words)
        
        # Update the message with remaining buttons
        selected_sentence = ' '.join(self.learning_state.get_selected_words(user_id))
        remaining_count = len(self.learning_state.get_current_sentence_words(user_id)) - len(self.learning_state.get_selected_words(user_id))
        
        await callback.message.edit_text(
            f"Selezione corrente: {selected_sentence}\n"
            f"Parole rimanenti: {remaining_count}",
            reply_markup=keyboard
        )
        await callback.answer()