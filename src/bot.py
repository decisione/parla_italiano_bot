import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import asyncio
import random
import logging
import os

from src.database import get_random_sentence, get_random_encouraging_phrase, get_random_error_phrase, get_schema_migrations, get_table_counts, get_or_create_user, store_sentence_result
from src.config import get_bot_config, get_logging_config

# User game state
user_game_state = {}

# Initialize bot with configuration
bot_config = get_bot_config()
bot = Bot(token=bot_config.token)
dp = Dispatcher()
router = Router()

def create_word_buttons(shuffled_words):
    """Create buttons for each word using the provided shuffled order"""
    keyboard_rows = []
    current_row = []
    
    for word in shuffled_words:
        current_row.append(types.InlineKeyboardButton(text=word, callback_data=f"word_{word}"))
        
        # Start a new row after every 4 buttons
        if len(current_row) == 4:
            keyboard_rows.append(current_row)
            current_row = []
    
    # Add any remaining buttons in the last row
    if current_row:
        keyboard_rows.append(current_row)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    return keyboard

@router.message(CommandStart())
async def start_game(message: Message):
    """Start the word ordering game"""
    user_id = message.from_user.id
    await get_or_create_user(message.from_user)
    await start_new_round(message, user_id)

async def start_new_round(message_or_callback, user_id):
    """Start a new round of the game"""
    # Get random sentence and store original order
    sentence_id, original_sentence = await get_random_sentence(user_id)
    words = original_sentence.split()
    random.shuffle(words)  # Shuffle once and store this order
    
    user_game_state[user_id] = {
        'sentence_id': sentence_id,
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
    await get_or_create_user(callback.from_user)
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
            emojis = ["🎉", "✅", "💣", "💥", "🥳", "🎆", "🎇", "🤩", "😎", "🥳", "💪", "👍", "🎈", "🎯", "🥇", "🏅", "🎖️", "🏆"]
            emoji = random.choice(emojis)
           
            await callback.message.edit_text(
                f"{emoji} {phrase} {emoji}\n<blockquote>{' '.join(original_words)}</blockquote>\n",
                parse_mode="HTML"
            )
            await callback.answer("Corretto!")
        else:
            # Select a random error phrase
            phrase = await get_random_error_phrase()
            emojis = ["❌", "✖️", "⚠️", "⁉️", "🆘", "🚫", "📛", "🛑", "⛔", "🌩️", "🪫", "🩻", "🧱", "🤚", "👎", "😞", "😪", "😣", "🥲"]
            emoji = random.choice(emojis)
            await callback.message.edit_text(
                f"{emoji} {phrase}\nLa tua risposta: <blockquote>{' '.join(selected_order)}</blockquote>\nOrdine corretto: <blockquote>{' '.join(original_words)}</blockquote>\n",
                parse_mode="HTML"
            )
            await callback.answer("Ordine sbagliato!")
        
        # Store the result
        sentence_id = user_game_state[user_id]['sentence_id']
        if sentence_id is not None:
            await store_sentence_result(user_id, sentence_id, original_words == selected_order)
        
        # Start next round after a short delay
        await asyncio.sleep(1)
        await start_new_round(callback.message, user_id)
    else:
        # Create keyboard with remaining buttons
        keyboard = create_word_buttons(remaining_words)
        
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
    await get_or_create_user(message.from_user)
    await message.answer(f"You said: {message.text}")

# Attach router to dispatcher
dp.include_router(router)

async def main():
    # Setup logging
    logging_config = get_logging_config()
    os.makedirs(logging_config.log_dir, exist_ok=True)
    log_file = os.path.join(logging_config.log_dir, 'bot.log')
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("Bot is starting...")
    logging.info("Connecting to database for init logging...")

    # Log schema migrations
    migrations = await get_schema_migrations()
    for migration in migrations:
        logging.info(f"Schema migration: {migration}")

    # Log table counts
    counts = await get_table_counts()
    for table, count in counts.items():
        logging.info(f"Table {table}: {count} rows")

    logging.info("Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())