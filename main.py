import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен берем из настроек Railway
API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Сюда вписывай ID покупателей (через запятую)
# Узнать свой ID можно у @userinfobot
vip_users = {7341841897} 

# Твой ID для команды /addvip
ADMIN_ID = 7341841897 

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💪 Моя тренировка", callback_data="workout"))
    builder.row(types.InlineKeyboardButton(text="🔥 Купить VIP", callback_data="buy_vip"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери действие:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "workout")
async def process_workout(callback: types.CallbackQuery):
    if callback.from_user.id in vip_users:
        await callback.message.answer("Твоя тренировка на сегодня: ...")
    else:
        await callback.message.answer("У тебя нет VIP. Напиши владельцу: @erastxx1")

@dp.callback_query(F.data == "buy_vip")
async def process_buy_vip(callback: types.CallbackQuery):
    await callback.message.answer("Чтобы купить VIP, напиши мне: @erastxx1")

# Команда для добавления VIP (писать боту: /addvip 987654321)
@dp.message(Command("addvip"))
async def add_vip(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            vip_users.add(user_id)
            await message.answer(f"Пользователь {user_id} добавлен в VIP!")
        except:
            await message.answer("Ошибка! Пиши так: /addvip ID_ПОЛЬЗОВАТЕЛЯ")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
