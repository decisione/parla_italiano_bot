from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Ciao, {message.from_user.full_name}!\n"
        "I'm your new bot built with aiogram 3! 🚀"
    )

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
