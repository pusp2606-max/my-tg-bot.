import os
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('dating_pro.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY, name TEXT, bio TEXT, photo_id TEXT, city TEXT)''')
conn.commit()

class Profile(StatesGroup):
    name = State(); city = State(); bio = State(); photo = State()

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Моя анкета", callback_data="my_profile")
    kb.button(text="🔍 Искать в Абхазии", callback_data="find_dating")
    return kb.as_markup()

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✨ **ERAST Dating — Номер 1 в Абхазии**\n\nВыбери действие:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "my_profile")
async def show_profile(callback: types.CallbackQuery):
    await callback.answer() # ОБЯЗАТЕЛЬНО: убирает "загрузку" на кнопке
    cursor.execute('SELECT * FROM users WHERE id = ?', (callback.from_user.id,))
    user = cursor.fetchone()
    if not user:
        await callback.message.answer("⚠️ У тебя нет анкеты. Напиши /register")
    else:
        await bot.send_photo(callback.from_user.id, user[3], caption=f"👤 **{user[1]}** ({user[4]})\n📝 {user[2]}")

@dp.callback_query(F.data == "find_dating")
async def find(callback: types.CallbackQuery):
    await callback.answer()
    user = cursor.execute('SELECT * FROM users WHERE id != ? ORDER BY RANDOM() LIMIT 1', (callback.from_user.id,)).fetchone()
    if not user:
        await callback.message.answer("Пока нет анкет. Расскажи друзьям!")
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="❤️ Лайк", callback_data=f"like_{user[0]}"); kb.button(text="👎 Дизлайк", callback_data="skip")
    await bot.send_photo(callback.from_user.id, user[3], caption=f"👤 **{user[1]}** ({user[4]})\n📝 {user[2]}", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("like_"))
async def like(callback: types.CallbackQuery):
    await callback.answer("Лайк поставлен!")
    await callback.message.delete()
    await find(callback)

@dp.callback_query(F.data == "skip")
async def skip(callback: types.CallbackQuery):
    await callback.answer("Пропуск")
    await callback.message.delete()
    await find(callback)

# Регистрация (Полный цикл)
@dp.message(Command("register"))
async def reg(message: types.Message, state: FSMContext):
    await message.answer("Как тебя зовут?"); await state.set_state(Profile.name)

@dp.message(Profile.name)
async def reg2(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text); await message.answer("Город?"); await state.set_state(Profile.city)

@dp.message(Profile.city)
async def reg3(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text); await message.answer("О себе:"); await state.set_state(Profile.bio)

@dp.message(Profile.bio)
async def reg4(message: types.Message, state: FSMContext):
    await state.update_data(bio=message.text); await message.answer("Фото:"); await state.set_state(Profile.photo)

@dp.message(Profile.photo)
async def reg5(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute('INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)', 
                   (message.from_user.id, data['name'], data['bio'], message.photo[-1].file_id, data['city']))
    conn.commit(); await message.answer("✅ Готово! Нажми /start"); await state.clear()

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
