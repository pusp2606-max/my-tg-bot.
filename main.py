import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Инициализация бота
API_TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# База данных
conn = sqlite3.connect('dating.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age TEXT, photo TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS likes (user_id INTEGER, liked_id INTEGER)')
conn.commit()

class Profile(StatesGroup):
    name = State(); age = State(); photo = State()

def get_vote_kb(user_id):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="❤️ Лайк", callback_data=f"like_{user_id}"))
    kb.row(types.InlineKeyboardButton(text="👎 Дизлайк", callback_data="skip"))
    return kb.as_markup()

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("👋 **Добро пожаловать в Dating Abkhazia!**\n\nДавай создадим твою анкету.\nКак тебя зовут?")
    await state.set_state(Profile.name)

@dp.message(Profile.name)
async def p_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Profile.age)

@dp.message(Profile.age)
async def p_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Пришли своё лучшее фото (одним файлом):")
    await state.set_state(Profile.photo)

@dp.message(Profile.photo)
async def p_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, пришли именно фото.")
        return
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    cursor.execute('INSERT OR REPLACE INTO users VALUES (?,?,?,?)', (message.from_user.id, data['name'], data['age'], photo_id))
    conn.commit()
    await message.answer("✅ **Анкета создана!**\n\nИспользуй команду /find, чтобы начать знакомиться!")
    await state.clear()

@dp.message(Command("find"))
async def find(message: types.Message):
    cursor.execute('SELECT * FROM users WHERE id != ? ORDER BY RANDOM() LIMIT 1', (message.from_user.id,))
    user = cursor.fetchone()
    if user:
        await bot.send_photo(message.chat.id, user[3], caption=f"👤 **{user[1]}**, {user[2]} лет", reply_markup=get_vote_kb(user[0]))
    else:
        await message.answer("Пока нет новых анкет. Расскажи друзьям о нашем боте!")

@dp.callback_query(F.data.startswith("like_"))
async def vote(callback: types.CallbackQuery):
    liked_id = int(callback.data.split("_")[1])
    cursor.execute('INSERT INTO likes VALUES (?,?)', (callback.from_user.id, liked_id))
    conn.commit()
    cursor.execute('SELECT * FROM likes WHERE user_id = ? AND liked_id = ?', (liked_id, callback.from_user.id))
    if cursor.fetchone():
        await bot.send_message(callback.from_user.id, f"🔥 **МЭТЧ!**\nПиши человеку: tg://user?id={liked_id}")
        await bot.send_message(liked_id, f"🔥 **МЭТЧ!**\nПиши человеку: tg://user?id={callback.from_user.id}")
    await callback.message.delete()
    await find(callback.message)

@dp.callback_query(F.data == "skip")
async def skip(callback: types.CallbackQuery):
    await callback.message.delete()
    await find(callback.message)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
