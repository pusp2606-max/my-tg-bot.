import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Токен берется из настроек Railway (Variables -> API_TOKEN)
API_TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список стран и цен (как на твоем скриншоте)
countries = {
    "🇵🇰 Pakistan": "$0.0050",
    "🇳🇪 Niger": "$0.0050",
    "🇬🇭 Ghana": "$0.0050",
    "🇳🇬 Nigeria Top 1": "$0.0050",
    "🇳🇬 Nigeria New": "$0.0050",
    "🇪🇹 Ethiopia": "$0.0050",
    "🇲🇿 Mozambique 2": "$0.0050",
    "🇪🇨 Ecuador 2": "$0.0060",
    "🇮🇶 IRAQ WS+FB 2": "$0.0050",
    "🇹🇯 Tajikistan 2": "$0.0050",
    "🇰🇬 Kyrgyzstan 2": "$0.0050"
}

# Создаем нижнюю панель кнопок
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📞 Get Number"), types.KeyboardButton(text="❓ Available Country"))
    builder.row(types.KeyboardButton(text="📊 Status"), types.KeyboardButton(text="💰 Balance"))
    builder.row(types.KeyboardButton(text="💸 Withdraw"), types.KeyboardButton(text="🌐 Live Traffic"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🛒 Добро пожаловать! Выберите услугу в меню внизу:", reply_markup=get_main_menu())

# Обработка кнопки "Available Country" (показывает список стран)
@dp.message(F.text == "❓ Available Country")
async def show_countries(message: types.Message):
    response = "🌎 **Доступные страны и цены:**\n\n"
    for country, price in countries.items():
        response += f"{country} | {price}/OTP\n"
    response += "\nДля покупки напишите владельцу: @erastxx1"
    await message.answer(response, parse_mode="Markdown")

@dp.message(F.text == "📞 Get Number")
async def get_number(message: types.Message):
    await message.answer("Для получения номера напишите владельцу: @erastxx1")

@dp.message(F.text == "💰 Balance")
async def show_balance(message: types.Message):
    await message.answer("Ваш баланс: 0 $")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
