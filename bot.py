import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎵 Отправь MP3, и я начну делать Hardtekk-ремикс."
    )

@dp.message()
async def audio(message: Message):
    if message.audio:
        await message.answer("⏳ Получил трек, начинаю обработку...")
        # Здесь позже будет вызов remix.py
        await message.answer("✅ Ремикс готов!")
    else:
        await message.answer("Пришли MP3-файл.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
