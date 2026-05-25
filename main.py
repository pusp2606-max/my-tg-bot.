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
                  (id INTEGER PRIMARY KEY, name TEXT, bio TEXT, photo_id TEXT, city TEXT, is_premium INTEGER DEFAULT 0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS likes (user_id INTEGER, liked_id INTEGER)''')
conn.commit()

class Profile(StatesGroup):
    name = State(); bio = State(); city = State(); photo = State()

# --- МЕНЮ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Моя анкета", callback_data="my_profile")
    kb.button(text="🔍 Искать в моем городе", callback_data="find_dating")
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
    await message.answer("✨ **ERAST Dating — Номер 1 в Абхазии**\n\n<i>Найди свою пару в своем городе.</i>", 
                         reply_markup=get_main_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "start")
async def back_to_start(callback: types.CallbackQuery):
    await start(callback.message)

@dp.callback_query(F.data == "my_profile")
async def show_profile(callback: types.CallbackQuery):
    cursor.execute('SELECT * FROM users WHERE id = ?', (callback.from_user.id,))
    user = cursor.fetchone()
    if not user: return await callback.message.answer("Анкета не найдена. Напиши /register")
    await bot.send_photo(callback.from_user.id, user[3], 
        caption=f"👤 **{user[1]}**, {user[4]}\n\n📝 *О себе:* {user[2]}",
        reply_markup=get_profile_kb(), parse_mode="Markdown")

@dp.message(Command("register"))
async def reg_start(message: types.Message, state: FSMContext):
    await message.answer("Как тебя зовут?"); await state.set_state(Profile.name)

@dp.message(Profile.name)
async def reg_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text); await message.answer("Твой город?"); await state.set_state(Profile.city)

@dp.message(Profile.city)
async def reg_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text); await message.answer("Расскажи о себе:"); await state.set_state(Profile.bio)

@dp.message(Profile.bio)
async def reg_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=message.text); await message.answer("Пришли фото:"); await state.set_state(Profile.photo)

@dp.message(Profile.photo)
async def reg_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    cursor.execute('INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)', (message.from_user.id, data['name'], data['bio'], photo_id, data['city'], 0))
    conn.commit()
    await message.answer("✅ **Профиль готов!** Нажми /start"); await state.clear()

@dp.callback_query(F.data == "find_dating")
async def find_dating(callback: types.CallbackQuery):
    cursor.execute('SELECT city FROM users WHERE id = ?', (callback.from_user.id,))
    res = cursor.fetchone()
    if not res: return await callback.message.answer("Сначала /register")
    city = res[0]
    cursor.execute('SELECT * FROM users WHERE id != ? AND city = ? ORDER BY RANDOM() LIMIT 1', (callback.from_user.id, city))
    user = cursor.fetchone()
    if user:
        kb = InlineKeyboardBuilder()
        kb.button(text="❤️ Лайк", callback_data=f"like_{user[0]}"); kb.button(text="👎 Дизлайк", callback_data="skip")
        await bot.send_photo(callback.from_user.id, user[3], caption=f"👤 **{user[1]}**, {user[4]}\n\n📝 *О себе:* {user[2]}", reply_markup=kb.as_markup(), parse_mode="Markdown")
    else:
        await callback.message.answer(f"В городе {city} пока пусто.")

@dp.callback_query(F.data.startswith("like_"))
async def vote(callback: types.CallbackQuery):
    liked_id = int(callback.data.split("_")[1])
    cursor.execute('INSERT INTO likes VALUES (?,?)', (callback.from_user.id, liked_id)); conn.commit()
    cursor.execute('SELECT * FROM likes WHERE user_id = ? AND liked_id = ?', (liked_id, callback.from_user.id))
    if cursor.fetchone():
        await bot.send_message(callback.from_user.id, f"🔥 **МЭТЧ!** Пиши: tg://user?id={liked_id}")
        await bot.send_message(liked_id, f"🔥 **МЭТЧ!** Пиши: tg://user?id={callback.from_user.id}")
    await callback.message.delete(); await find_dating(callback)

@dp.callback_query(F.data == "skip")
async def skip(callback: types.CallbackQuery):
    await callback.message.delete(); await find_dating(callback)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
