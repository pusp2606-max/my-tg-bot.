import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from remix import make_remix
import os

from config import BOT_TOKEN

print("TOKEN =", BOT_TOKEN)   # ← добавь эту строку

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎵 Отправь MP3, и я начну делать Hardtekk-ремикс."
    )


@dp.message()
async def audio(message: Message):
    if not message.audio:
        await message.answer("🎵 Пришли MP3-файл.")
        return

    os.makedirs("downloads", exist_ok=True)

    telegram_file = await bot.get_file(message.audio.file_id)
    input_path = f"downloads/{message.audio.file_name}"

    await bot.download_file(
        telegram_file.file_path,
        destination=input_path
    )

    await message.answer("⏳ Создаю ремикс...")

    output = make_remix(input_path)

    audio = FSInputFile(output)

    await message.answer_audio(
        audio,
        caption="🔥 Hardtekk Remix Ready!"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
