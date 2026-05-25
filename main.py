import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ВСТАВЬ СЮДА СВОЙ ТОКЕН
API_TOKEN = 8881931249:AAECg8Uv_o8nrs1fOd99KiuFi_PPvHt6T6A'ВСТАВЬ_СЮЖЕ_СВОЙ_ТОКЕН_ОТ_BOTFATHER'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем клавиатуру с кнопками для заработка
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Моя тренировка (Бесплатно)", callback_data="workout")],
        [InlineKeyboardButton(text="🔥 Купить VIP-план (100 руб)", callback_data="buy_vip")]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я твой бот-ассистент. Выбери действие:", reply_markup=get_main_keyboard())

# Обработка нажатий на кнопки
@dp.callback_query(F.data == "workout")
async def send_workout(callback: types.CallbackQuery):
    await callback.message.answer("Твоя задача на сегодня: 50 отжиманий! Не сдавайся!")
    await callback.answer()

@dp.callback_query(F.data == "buy_vip")
async def buy_vip(callback: types.CallbackQuery):
    # Здесь можно будет подключить оплату (Telegram Stars или юкасса)
    await callback.message.answer("Чтобы купить VIP, напиши моему владельцу: @erastxx1")
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())