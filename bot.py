=========================

APSNY LOVE FULL VERSION

=========================

import sqlite3
import random
import os
import datetime

from telegram import ReplyKeyboardMarkup
from telegram.ext import (
Updater,
CommandHandler,
MessageHandler,
Filters
)

TOKEN = os.getenv("BOT_TOKEN")

conn = sqlite3.connect(
"dating.db",
check_same_thread=False
)

cursor = conn.cursor()

=========================

DATABASE

=========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
username TEXT,
name TEXT,
age TEXT,
gender TEXT,
city TEXT,
bio TEXT,
music TEXT,
mood TEXT,
photo TEXT,
tags TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
from_user INTEGER,
to_user INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
user_id INTEGER,
favorite_id INTEGER
)
""")

conn.commit()

=========================

KEYBOARDS

=========================

menu = ReplyKeyboardMarkup(
[
["🔍 Смотреть анкеты"],
["🌊 Настроение", "💘 Crush дня"],
["🌙 Night Match", "🎵 Музыкальный вайб"],
["👤 Моя анкета", "❤️ Избранное"],
["✏️ Изменить анкету"],
["🗑 Удалить анкету"],
["📊 Статистика", "ℹ️ Помощь"]
],
resize_keyboard=True
)

like_menu = ReplyKeyboardMarkup(
[
["❤️", "👎"],
["👀 Кто лайкнул"],
["⭐ В избранное"],
["🏠 Главное меню"]
],
resize_keyboard=True
)

mood_keyboard = ReplyKeyboardMarkup(
[
["❤️ Ищу любовь"],
["🌊 Хочу общения"],
["🎮 Ищу друзей"],
["☕ Погулять"],
["🌙 Поболтать ночью"]
],
resize_keyboard=True
)

city_keyboard = ReplyKeyboardMarkup(
[
["📍 Сухум", "📍 Гагра"],
["📍 Гудаута", "📍 Пицунда"],
["📍 Очамчыра", "📍 Гал"],
["📍 Ткварчал", "📍 Адлер"],
["📍 Сочи"]
],
resize_keyboard=True
)

tags_keyboard = ReplyKeyboardMarkup(
[
["💪 Спорт", "🎮 Игры"],
["🎵 Музыка", "🎬 Фильмы"],
["☕ Прогулки", "📸 Фото"],
["🌙 Ночные вайбы", "🚗 Машины"]
],
resize_keyboard=True
)

register_step = {}
temp_data = {}
last_profile = {}

=========================

START

=========================

def start(update, context):

uid = update.message.from_user.id

register_step[uid] = "name"
temp_data[uid] = {}

update.message.reply_text(
    "🌊 Добро пожаловать в Apsny Love ❤️\n\n"
    "Как тебя зовут?"
)

=========================

TEXT HANDLER

=========================

def text_handler(update, context):

uid = update.message.from_user.id
text = update.message.text

moods = [
    "❤️ Ищу любовь",
    "🌊 Хочу общения",
    "🎮 Ищу друзей",
    "☕ Погулять",
    "🌙 Поболтать ночью"
]

if text in moods:

    temp_data.setdefault(uid, {})
    temp_data[uid]["mood"] = text

    update.message.reply_text(
        f"✨ Настроение установлено:\n\n{text}",
        reply_markup=menu
    )

    return

if text == "🔍 Смотреть анкеты":
    show_profile(update, context)
    return

if text == "👤 Моя анкета":
    my_profile(update, context)
    return

if text == "❤️ Избранное":
    favorites(update, context)
    return

if text == "✏️ Изменить анкету":
    edit_profile(update, context)
    return

if text == "🗑 Удалить анкету":
    delete_profile(update, context)
    return

if text == "🌊 Настроение":

    update.message.reply_text(
        "✨ Выбери настроение",
        reply_markup=mood_keyboard
    )

    return

if text == "💘 Crush дня":
    crush_day(update, context)
    return

if text == "🌙 Night Match":
    night_match(update, context)
    return

if text == "🎵 Музыкальный вайб":
    music_vibe(update, context)
    return

if text == "📊 Статистика":
    stats(update, context)
    return

if text == "ℹ️ Помощь":
    help_command(update, context)
    return

if text == "🏠 Главное меню":

    update.message.reply_text(
        "🏠 Главное меню",
        reply_markup=menu
    )

    return

# LIKE SYSTEM

if text == "❤️":
    like(update, context)
    return

if text == "👎":
    skip(update, context)
    return

if text == "👀 Кто лайкнул":
    view_likes(update, context)
    return

if text == "⭐ В избранное":
    add_favorite(update, context)
    return

# REGISTER

if uid not in register_step:
    return

step = register_step[uid]

if step == "name":

    temp_data[uid]["name"] = text
    register_step[uid] = "age"

    update.message.reply_text(
        "Сколько тебе лет?"
    )

elif step == "age":

    temp_data[uid]["age"] = text
    register_step[uid] = "gender"

    update.message.reply_text(
        "Твой пол?\n\nМ или Ж"
    )

elif step == "gender":

    temp_data[uid]["gender"] = text
    register_step[uid] = "city"

    update.message.reply_text(
        "📍 Выбери город",
        reply_markup=city_keyboard
    )

elif step == "city":

    temp_data[uid]["city"] = text.replace("📍 ", "")
    register_step[uid] = "bio"

    update.message.reply_text(
        "📝 Напиши описание о себе"
    )

elif step == "bio":

    temp_data[uid]["bio"] = text
    register_step[uid] = "tags"

    update.message.reply_text(
        "✨ Выбери интерес",
        reply_markup=tags_keyboard
    )

elif step == "tags":

    temp_data[uid]["tags"] = text
    register_step[uid] = "music"

    update.message.reply_text(
        "🎵 Любимая песня или артист?"
    )

elif step == "music":

    temp_data[uid]["music"] = text
    register_step[uid] = "photo"

    update.message.reply_text(
        "Теперь отправь фото 📸"
    )

=========================

PHOTO

=========================

def photo_handler(update, context):

uid = update.message.from_user.id

if uid not in register_step:
    return

if register_step[uid] != "photo":
    return

try:

    photo = update.message.photo[-1].file_id

    username = update.message.from_user.username

    data = temp_data[uid]

    mood = data.get(
        "mood",
        "🌊 Без настроения"
    )

    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        username,
        data["name"],
        data["age"],
        data["gender"],
        data["city"],
        data["bio"],
        data["music"],
        mood,
        photo,
        data.get("tags", "Без интересов")
    ))

    conn.commit()

    del register_step[uid]

    update.message.reply_text(
        "✅ Анкета сохранена",
        reply_markup=menu
    )

except Exception as e:
    print(e)

=========================

SHOW PROFILE

=========================

def show_profile(update, context):

uid = update.message.from_user.id

cursor.execute("""
SELECT city
FROM users
WHERE user_id=?
""", (uid,))

my_city = cursor.fetchone()

if my_city:

    my_city = my_city[0]

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id != ?
    AND city=?
    ORDER BY RANDOM()
    LIMIT 1
    """, (uid, my_city))

else:

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id != ?
    ORDER BY RANDOM()
    LIMIT 1
    """, (uid,))

target = cursor.fetchone()

if not target:

    update.message.reply_text(
        "😢 Анкет пока нет"
    )

    return

last_profile[uid] = target[0]

username = target[1]

if username:
    username_text = f"\n📱 @{username}"
else:
    username_text = ""

text = f"""

❤️ {target[2]}, {target[3]}
🚻 {target[4]}
📍 {target[5]}

📝 {target[6]}

🎵 {target[7]}
✨ {target[8]}
🏷 {target[10]}
{username_text}
"""

try:

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=target[9],
        caption=text,
        reply_markup=like_menu
    )

except Exception as e:
    print(e)

=========================

VIEW LIKES

=========================

def view_likes(update, context):

uid = update.message.from_user.id

cursor.execute("""
SELECT from_user
FROM likes
WHERE to_user=?
ORDER BY ROWID DESC
""", (uid,))

likes = cursor.fetchall()

if not likes:

    update.message.reply_text(
        "❤️ Тебя пока никто не лайкнул"
    )

    return

target_id = likes[0][0]

cursor.execute("""
SELECT *
FROM users
WHERE user_id=?
""", (target_id,))

user = cursor.fetchone()

if not user:
    return

last_profile[uid] = target_id

username = user[1]

if username:
    username_text = f"\n📱 @{username}"
else:
    username_text = "\n📱 Юзер не указан"

text = f"""

👀 Тебя лайкнул(а):

❤️ {user[2]}, {user[3]}
🚻 {user[4]}
📍 {user[5]}

📝 {user[6]}

🎵 {user[7]}
✨ {user[8]}
🏷 {user[10]}
{username_text}
"""

try:

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=user[9],
        caption=text,
        reply_markup=like_menu
    )

except Exception as e:
    update.message.reply_text(str(e))
    print(e)

=========================

LIKE

=========================

def like(update, context):

uid = update.message.from_user.id

if uid not in last_profile:
    return

target = last_profile[uid]

cursor.execute("""
INSERT INTO likes
VALUES (?, ?)
""", (uid, target))

conn.commit()

try:

    context.bot.send_message(
        chat_id=target,
        text="❤️ Кому-то понравилась твоя анкета\n\nНажми «👀 Кто лайкнул»"
    )

except:
    pass

cursor.execute("""
SELECT * FROM likes
WHERE from_user=? AND to_user=?
""", (target, uid))

match = cursor.fetchone()

if match:

    cursor.execute("""
    SELECT username
    FROM users
    WHERE user_id=?
    """, (target,))

    user = cursor.fetchone()

    username = user[0]

    if username:

        update.message.reply_text(
            f"💘 Это взаимный лайк!\n\n@{username}"
        )

        sender_username = update.message.from_user.username

        if sender_username:

            context.bot.send_message(
                chat_id=target,
                text=f"💘 Это взаимный лайк!\n\n@{sender_username}"
            )

    else:

        update.message.reply_text(
            "💘 Это взаимный лайк!"
        )

else:

    update.message.reply_text(
        "❤️ Лайк отправлен"
    )

show_profile(update, context)

=========================

SKIP

=========================

def skip(update, context):
show_profile(update, context)

=========================

FAVORITES

=========================

def add_favorite(update, context):

uid = update.message.from_user.id

if uid not in last_profile:
    return

target = last_profile[uid]

cursor.execute("""
INSERT INTO favorites
VALUES (?, ?)
""", (uid, target))

conn.commit()

update.message.reply_text(
    "⭐ Добавлено в избранное"
)

=========================

FAVORITES LIST

=========================

def favorites(update, context):

uid = update.message.from_user.id

cursor.execute("""
SELECT favorite_id
FROM favorites
WHERE user_id=?
""", (uid,))

favs = cursor.fetchall()

if not favs:

    update.message.reply_text(
        "❤️ Избранное пусто"
    )

    return

text = "❤️ Избранное:\n\n"

for fav in favs:

    cursor.execute("""
    SELECT name, age, city
    FROM users
    WHERE user_id=?
    """, (fav[0],))

    user = cursor.fetchone()

    if user:

        text += f"""

❤️ {user[0]}, {user[1]}
📍 {user[2]}

"""

update.message.reply_text(text)

=========================

MY PROFILE

=========================

def my_profile(update, context):

uid = update.message.from_user.id

cursor.execute("""
SELECT * FROM users
WHERE user_id=?
""", (uid,))

user = cursor.fetchone()

if not user:

    update.message.reply_text(
        "У тебя нет анкеты"
    )

    return

username = user[1]

if username:
    username_text = f"\n📱 @{username}"
else:
    username_text = ""

text = f"""

👤 Твоя анкета

❤️ {user[2]}, {user[3]}
🚻 {user[4]}
📍 {user[5]}

📝 {user[6]}

🎵 {user[7]}
✨ {user[8]}
🏷 {user[10]}
{username_text}
"""

try:

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=user[9],
        caption=text,
        reply_markup=menu
    )

except:
    pass

=========================

DELETE PROFILE

=========================

def delete_profile(update, context):

uid = update.message.from_user.id

cursor.execute("""
DELETE FROM users
WHERE user_id=?
""", (uid,))

cursor.execute("""
DELETE FROM likes
WHERE from_user=? OR to_user=?
""", (uid, uid))

cursor.execute("""
DELETE FROM favorites
WHERE user_id=? OR favorite_id=?
""", (uid, uid))

conn.commit()

update.message.reply_text(
    "🗑 Твоя анкета удалена",
    reply_markup=menu
)

=========================

EDIT PROFILE

=========================

def edit_profile(update, context):

uid = update.message.from_user.id

register_step[uid] = "name"
temp_data[uid] = {}

update.message.reply_text(
    "✏️ Введи новое имя"
)

=========================

CRUSH DAY

=========================

def crush_day(update, context):

cursor.execute("""
SELECT * FROM users
ORDER BY RANDOM()
LIMIT 1
""")

user = cursor.fetchone()

if not user:
    return

username = user[1]

if username:
    username_text = f"\n📱 @{username}"
else:
    username_text = ""

text = f"""

💘 Crush дня

❤️ {user[2]}, {user[3]}
📍 {user[5]}

🎵 {user[7]}
🏷 {user[10]}
{username_text}
"""

try:

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=user[9],
        caption=text,
        reply_markup=menu
    )

except:
    pass

=========================

NIGHT MATCH

=========================

def night_match(update, context):

hour = datetime.datetime.now().hour

if hour >= 23 or hour <= 5:

    update.message.reply_text(
        "🌙 Night Match активирован"
    )

    show_profile(update, context)

else:

    update.message.reply_text(
        "🌙 Night Match работает после 23:00"
    )

=========================

MUSIC VIBE

=========================

def music_vibe(update, context):

uid = update.message.from_user.id

cursor.execute("""
SELECT music
FROM users
WHERE user_id=?
""", (uid,))

my_music = cursor.fetchone()

if not my_music:

    update.message.reply_text(
        "Сначала создай анкету"
    )

    return

my_music = my_music[0].lower()

cursor.execute("""
SELECT *
FROM users
WHERE user_id != ?
""", (uid,))

users = cursor.fetchall()

matched = []

for user in users:

    try:

        other_music = str(user[7]).lower()

        if my_music in other_music or other_music in my_music:
            matched.append(user)

    except:
        pass

if not matched:

    update.message.reply_text(
        "🎵 Пока нет людей с похожим вайбом"
    )

    return

target = random.choice(matched)

username = target[1]

if username:
    username_text = f"\n📱 @{username}"
else:
    username_text = ""

text = f"""

🎵 Музыкальный вайб совпал

❤️ {target[2]}, {target[3]}
📍 {target[5]}

🎧 Любит: {target[7]}
🏷 {target[10]}
{username_text}
"""

try:

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=target[9],
        caption=text,
        reply_markup=like_menu
    )

except:
    pass

=========================

HELP

=========================

def help_command(update, context):

update.message.reply_text(
    "🌊 Apsny Love ❤️\n\n"
    "❤️ Лайки\n"
    "💘 Матчи\n"
    "🌍 Поиск по городу\n"
    "🏷 Интересы\n"
    "🌙 Night Match\n"
    "🎵 Музыкальный вайб\n"
    "⭐ Избранное"
)

=========================

STATS

=========================

def stats(update, context):

cursor.execute("""
SELECT COUNT(*)
FROM users
""")

users = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM likes
""")

likes = cursor.fetchone()[0]

update.message.reply_text(
    f"📊 Статистика\n\n"
    f"👤 Пользователей: {users}\n"
    f"❤️ Лайков: {likes}"
)

=========================

START BOT

=========================

print("BOT STARTED")

updater = Updater(
TOKEN,
use_context=True
)

dp = updater.dispatcher

dp.add_handler(
CommandHandler(
"start",
start
)
)

dp.add_handler(
MessageHandler(
Filters.text,
text_handler
)
)

dp.add_handler(
MessageHandler(
Filters.photo,
photo_handler
)
)

updater.start_polling()
updater.idle()
