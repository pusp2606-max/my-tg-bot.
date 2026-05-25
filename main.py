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
conn = sqlite3.connect('dating_pro.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY, name TEXT, bio TEXT, photo_id TEXT, city TEXT, is_premium INTEGER DEFAULT 0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS likes (user_id INTEGER, liked_id INTEGER)''')
conn.commit()

class Profile(StatesGroup):
    name = State(); bio = State(); city = State(); photo = State()

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Моя анкета", callback_data="my_profile")
    kb.button(text="🔍 Искать в городе", callback_data="find_dating")
    kb.row(types.InlineKeyboardButton(text="⭐ Premium", callback_data="premium"),
           types.InlineKeyboardButton(text="🚫 Жалоба", callback_data="report"))
    return kb.as_markup()

def get_profile_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Заполнить заново", callback_data="register_again")
    kb.button(text="🖼 Изменить фото", callback_data="edit_photo")
    kb.button(text="✏️ Изменить текст", callback_data="edit_bio")
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="start"))
    return kb.as_markup()

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✨ **ERAST Dating — Номер 1 в Абхазии**\n\nНайди свою пару прямо сейчас.", 
                         reply_markup=get_main_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "start")
async def back(callback: types.CallbackQuery): await start(callback.message)

@dp.callback_query(F.data == "my_profile")
async def show_profile(callback: types.CallbackQuery):
    cursor.execute('SELECT * FROM users WHERE id = ?', (callback.from_user.id,))
    user = cursor.fetchone()
    if not user: return await callback.message.answer("⚠️ Нет анкеты. Напиши /register")
    await bot.send_photo(callback.from_user.id, user[3], 
        caption=f"👤 **{user[1]}**, {user[4]}\n\n📝 *О себе:* {user[2]}",
        reply_markup=get_profile_kb(), parse_mode="Markdown")

# Редактирование
@dp.callback_query(F.data == "edit_bio")
async def edit_bio(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("✏️ Напиши новый текст:"); await state.set_state(Profile.bio)

@dp.message(Profile.bio)
async def update_bio(message: types.Message, state: FSMContext):
    cursor.execute('UPDATE users SET bio = ? WHERE id = ?', (message.text, message.from_user.id)); conn.commit()
    await message.answer("✅ Обновлено!"); await state.clear()

@dp.callback_query(F.data == "edit_photo")
async def edit_photo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🖼 Пришли новое фото:"); await state.set_state(Profile.photo)

@dp.message(Profile.photo)
async def update_photo(message: types.Message, state: FSMContext):
    cursor.execute('UPDATE users SET photo_id = ? WHERE id = ?', (message.photo[-1].file_id, message.from_user.id)); conn.commit()
    await message.answer("✅ Фото обновлено!"); await state.clear()

# Регистрация (полная)
@dp.message(Command("register"))
async def reg(message: types.Message, state: FSMContext):
    await message.answer("Как зовут?"); await state.set_state(Profile.name)

@dp.message(Profile.name)
async def reg_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text); await message.answer("Город?"); await state.set_state(Profile.city)

@dp.message(Profile.city)
async def reg_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text); await message.answer("О себе:"); await state.set_state(Profile.bio)

@dp.message(Profile.bio)
async def reg_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=message.text); await message.answer("Фото:"); await state.set_state(Profile.photo)

@dp.message(Profile.photo)
async def reg_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute('INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)', 
                   (message.from_user.id, data['name'], data['bio'], message.photo[-1].file_id, data['city'], 0))
    conn.commit(); await message.answer("✅ Профиль готов! /start"); await state.clear()

# Поиск
@dp.callback_query(F.data == "find_dating")
async def find(callback: types.CallbackQuery):
    res = cursor.execute('SELECT city FROM users WHERE id = ?', (callback.from_user.id,)).fetchone()
    if not res: return await callback.message.answer("Сначала /register")
    user = cursor.execute('SELECT * FROM users WHERE id != ? AND city = ? ORDER BY RANDOM() LIMIT 1', (callback.from_user.id, res[0])).fetchone()
    if user:
        kb = InlineKeyboardBuilder()
        kb.button(text="❤️ Лайк", callback_data=f"like_{user[0]}"); kb.button(text="👎 Дизлайк", callback_data="skip")
        await bot.send_photo(callback.from_user.id, user[3], caption=f"👤 {user[1]}, {user[4]}\n📝 {user[2]}", reply_markup=kb.as_markup())
    else: await callback.message.answer("В твоем городе пока пусто.")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
