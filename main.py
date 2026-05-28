import os
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Инициализация
bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())

# База данных
conn = sqlite3.connect('erast_dating.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY, name TEXT, bio TEXT, photo_id TEXT, city TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS likes (user_id INTEGER, liked_id INTEGER)''')
conn.commit()

class Profile(StatesGroup):
    name = State(); city = State(); bio = State(); photo = State()

# --- КЛАВИАТУРЫ ---
def main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Моя анкета", callback_data="my_profile")
    kb.button(text="🔍 Искать в Абхазии", callback_data="find_dating")
    return kb.as_markup()

def profile_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Заполнить заново", callback_data="reg_again")
    kb.button(text="🖼 Изменить фото", callback_data="edit_photo")
    kb.button(text="✏️ Изменить текст", callback_data="edit_bio")
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="start"))
    return kb.as_markup()

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✨ **ERAST Dating — Номер 1 в Абхазии**\n\nВыбери действие:", reply_markup=main_kb())

@dp.callback_query(F.data == "start")
async def back(callback: types.CallbackQuery): await start(callback.message)

# Регистрация (Полный цикл)
@dp.message(Command("register"))
async def reg_start(message: types.Message, state: FSMContext):
    await message.answer("Как тебя зовут?"); await state.set_state(Profile.name)

@dp.message(Profile.name)
async def reg_city(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text); await message.answer("Из какого ты города?"); await state.set_state(Profile.city)

@dp.message(Profile.city)
async def reg_bio(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text); await message.answer("Напиши о себе:"); await state.set_state(Profile.bio)

@dp.message(Profile.bio)
async def reg_photo(message: types.Message, state: FSMContext):
    await state.update_data(bio=message.text); await message.answer("Пришли лучшее фото:"); await state.set_state(Profile.photo)

@dp.message(Profile.photo)
async def reg_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute('INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)', 
                   (message.from_user.id, data['name'], data['bio'], message.photo[-1].file_id, data['city']))
    conn.commit(); await message.answer("✅ **Профиль активирован!** Нажми /start"); await state.clear()

# Поиск
@dp.callback_query(F.data == "find_dating")
async def find(callback: types.CallbackQuery):
    user = cursor.execute('SELECT * FROM users WHERE id != ? ORDER BY RANDOM() LIMIT 1', (callback.from_user.id,)).fetchone()
    if not user: return await callback.message.answer("Пока нет анкет. Расскажи друзьям!")
    kb = InlineKeyboardBuilder()
    kb.button(text="❤️ Лайк", callback_data=f"like_{user[0]}"); kb.button(text="👎 Дизлайк", callback_data="skip")
    await bot.send_photo(callback.from_user.id, user[3], caption=f"👤 **{user[1]}** ({user[4]})\n📝 {user[2]}", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("like_"))
async def like(callback: types.CallbackQuery):
    liked_id = int(callback.data.split("_")[1])
    cursor.execute('INSERT INTO likes VALUES (?,?)', (callback.from_user.id, liked_id)); conn.commit()
    await callback.message.delete(); await find(callback)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
