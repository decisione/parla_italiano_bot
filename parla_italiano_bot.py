from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import asyncio
import os
import random
from dotenv import load_dotenv
from database import get_random_sentence, get_random_encouraging_phrase, get_random_error_phrase

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# User game state
user_game_state = {}

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
router = Router()

def create_word_buttons(shuffled_words):
    """Create buttons for each word using the provided shuffled order"""
    buttons = []
    for word in shuffled_words:
        buttons.append(types.InlineKeyboardButton(text=word, callback_data=f"word_{word}"))
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

@router.message(CommandStart())
async def start_game(message: Message):
    """Start the word ordering game"""
    user_id = message.from_user.id
    await start_new_round(message, user_id)

async def start_new_round(message_or_callback, user_id):
    """Start a new round of the game"""
    # Get random sentence and store original order
    original_sentence = await get_random_sentence()
    words = original_sentence.split()
    random.shuffle(words)  # Shuffle once and store this order
    
    user_game_state[user_id] = {
        'original_sentence': original_sentence,
        'selected_words': [],
        'current_sentence_words': original_sentence.split(),
        'shuffled_words': words  # Store the shuffled order
    }
    
    # Create buttons with words in the shuffled order
    keyboard = create_word_buttons(words)
    
    if hasattr(message_or_callback, 'message'):
        # It's a callback query
        await message_or_callback.answer()
        await message_or_callback.message.edit_text(
            f"Disponi queste parole per formare la frase italiana corretta:",
            reply_markup=keyboard
        )
    else:
        # It's a message
        await message_or_callback.answer(
            f"Disponi queste parole per formare la frase italiana corretta:",
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith("word_"))
async def handle_word_selection(callback: CallbackQuery):
    """Handle word button clicks"""
    user_id = callback.from_user.id
    selected_word = callback.data.replace("word_", "")
    
    if user_id not in user_game_state:
        await callback.answer("Per favore, avvia prima il gioco con /start")
        return
    
    # Add selected word to user's selection
    user_game_state[user_id]['selected_words'].append(selected_word)
    
    # Remove the button that was clicked, maintaining the original shuffled order
    remaining_words = [word for word in user_game_state[user_id]['shuffled_words']
                      if word not in user_game_state[user_id]['selected_words']]
    
    # Check if all words have been selected
    if len(user_game_state[user_id]['selected_words']) == len(user_game_state[user_id]['current_sentence_words']):
        # Check if the order is correct
        original_words = user_game_state[user_id]['current_sentence_words']
        selected_order = user_game_state[user_id]['selected_words']
        
        if original_words == selected_order:
            # Select a random encouraging phrase
            phrase = await get_random_encouraging_phrase()
            await callback.message.edit_text(f"{phrase} 🎉")
            await callback.answer("Corretto!")
        else:
            # Select a random error phrase
            phrase = await get_random_error_phrase()
            await callback.message.edit_text(f"{phrase} ❌ \nL'ordine corretto era: {' '.join(original_words)}")
            await callback.answer("Ordine sbagliato!")
        
        # Start next round after a short delay
        await asyncio.sleep(1)
        await start_new_round(callback.message, user_id)
    else:
        # Create keyboard with remaining buttons
        buttons = []
        for word in remaining_words:
            buttons.append(types.InlineKeyboardButton(text=word, callback_data=f"word_{word}"))
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
        
        # Update the message with remaining buttons
        selected_sentence = ' '.join(user_game_state[user_id]['selected_words'])
        remaining_count = len(user_game_state[user_id]['current_sentence_words']) - len(user_game_state[user_id]['selected_words'])
        
        await callback.message.edit_text(
            f"Selezione corrente: {selected_sentence}\n"
            f"Parole rimanenti: {remaining_count}",
            reply_markup=keyboard
        )
        await callback.answer()

@router.message()
async def echo(message: Message):
    await message.answer(f"You said: {message.text}")

# Attach router to dispatcher
dp.include_router(router)

async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
