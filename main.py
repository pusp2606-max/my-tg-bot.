import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

API_TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список стран с ценами (на русском)
countries = {
    "🇵🇰 Пакистан": "$0.0050", "🇳🇪 Нигер": "$0.0050", "🇬🇭 Гана": "$0.0050",
    "🇳🇬 Нигерия (Топ 1)": "$0.0050", "🇳🇬 Нигерия (Новые)": "$0.0050", "🇪🇹 Эфиопия": "$0.0050",
    "🇲🇿 Мозамбик 2": "$0.0050", "🇪🇨 Эквадор 2": "$0.0060", "🇮🇶 Ирак WS+FB 2": "$0.0050",
    "🇹🇯 Таджикистан 2": "$0.0050", "🇰🇬 Кыргызстан 2": "$0.0050"
}

# Нижняя панель (переведена)
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📞 Получить номер"), types.KeyboardButton(text="❓ Доступные страны"))
    builder.row(types.KeyboardButton(text="📊 Статус"), types.KeyboardButton(text="💰 Баланс"))
    builder.row(types.KeyboardButton(text="💸 Вывод средств"), types.KeyboardButton(text="🌐 Live Traffic"))
    return builder.as_markup(resize_keyboard=True)

# Выбор сервиса
@dp.message(F.text == "📞 Получить номер")
async def get_number(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔵 WhatsApp 1", callback_data="svc_wa1"))
    builder.row(types.InlineKeyboardButton(text="🔵 WhatsApp 2", callback_data="svc_wa2"))
    await message.answer("Выберите сервис:", reply_markup=builder.as_markup())

# Выбор страны
@dp.callback_query(F.data.startswith("svc_"))
async def choose_country(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for name, price in countries.items():
        # Заменяем пробелы на подчеркивания для технической части
        builder.row(types.InlineKeyboardButton(text=f"{name} | {price}", callback_data=f"cty_{name.replace(' ', '_')}"))
    await callback.message.edit_text("Выберите страну:", reply_markup=builder.as_markup())

# Финал
@dp.callback_query(F.data.startswith("cty_"))
async def final_step(callback: types.CallbackQuery):
    country = callback.data.split("_")[1].replace("_", " ")
    await callback.message.edit_text(f"✅ Вы выбрали: {country}\n\nДля покупки напишите владельцу: @erastxx1")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в панель управления!", reply_markup=get_main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
