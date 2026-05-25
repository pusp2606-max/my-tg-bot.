import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Берем бейджик (токен) из настроек Railway
token = os.getenv('API_TOKEN')
bot = Bot(token=token)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот работает! Я на связи!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
