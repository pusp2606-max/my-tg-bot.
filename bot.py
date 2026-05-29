# =========================
# APSNY LOVE FULL FIXED VERSION
# =========================

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

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "dating.db",
    check_same_thread=False
)

cursor = conn.cursor()

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
    tags TEXT,
    vip INTEGER DEFAULT 0
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

# =========================
# KEYBOARDS
# =========================

menu = ReplyKeyboardMarkup(
    [
        ["🔍 Смотреть анкеты"],
        ["👀 Кто лайкнул", "💘 Crush дня"],
        ["⭐ Избранное", "🏆 Топ недели"],
        ["🌙 Night Match", "🎵 Музыкальный вайб"],
        ["🌊 Настроение", "📊 Статистика"],
        ["👤 Моя анкета", "👑 VIP"],
        ["✏️ Изменить анкету"],
        ["🗑 Удалить анкету", "ℹ️ Помощь"]
    ],
    resize_keyboard=True
)

like_menu = ReplyKeyboardMarkup(
    [
        ["❤️", "👎"],
        ["⭐ В избранное"],
        ["🏠 Главное меню"]
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

register_step = {}
temp_data = {}
last_profile = {}

# =========================
# START
# =========================

def start(update, context):

    uid = update.message.from_user.id

    register_step[uid] = "name"
    temp_data[uid] = {}

    update.message.reply_text(
        "💎 Добро пожаловать в Apsny Love Premium 💎\n\n"
        "🌊 Самый красивый бот знакомств Абхазии\n"
        "❤️ Лайки • Матчи • Night Match • Crush дня\n\n"
        "✨ Найди человека по вайбу\n\n"
        "👤 Как тебя зовут?"
    )

# =========================
# TEXT HANDLER
# =========================

def text_handler(update, context):

    uid = update.message.from_user.id
    text = update.message.text

    # MENU

    if text == "🔍 Смотреть анкеты":
        show_profile(update, context)
        return

    if text == "👀 Кто лайкнул":
        view_likes(update, context)
        return

    if text == "⭐ Избранное":
        favorites(update, context)
        return

    if text == "💘 Crush дня":
        crush_day(update, context)
        return

    if text == "🏆 Топ недели":
        top_users(update, context)
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

    if text == "👤 Моя анкета":
        my_profile(update, context)
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

    if text == "👑 VIP":

        update.message.reply_text(
            "👑 VIP скоро появится 🔥"
        )

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

    if text == "⭐ В избранное":
        add_favorite(update, context)
        return

    # MOODS

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

    # REGISTER

    if uid not in register_step:
        return

    step = register_step[uid]

    if step == "name":

        temp_data[uid]["name"] = text
        register_step[uid] = "age"

        update.message.reply_text(
            "❤️ Сколько тебе лет?"
        )

    elif step == "age":

        temp_data[uid]["age"] = text
        register_step[uid] = "gender"

        update.message.reply_text(
            "🚻 Твой пол?\n\nМ или Ж"
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
            "🏷 Выбери интерес",
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
            "📸 Отправь фото"
        )

# =========================
# PHOTO
# =========================

def photo_handler(update, context):

    uid = update.message.from_user.id

    if uid not in register_step:
        return

    if register_step[uid] != "photo":
        return

    photo = update.message.photo[-1].file_id

    username = update.message.from_user.username

    data = temp_data[uid]

    mood = data.get(
        "mood",
        "🌊 Без настроения"
    )

    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        data["tags"],
        0
    ))

    conn.commit()

    del register_step[uid]

    update.message.reply_text(
        "✅ Анкета сохранена",
        reply_markup=menu
    )

# =========================
# SHOW PROFILE FIXED
# =========================

def show_profile(update, context):

    uid = update.message.from_user.id

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id != ?
    ORDER BY RANDOM()
    LIMIT 1
    """, (uid,))

    user = cursor.fetchone()

    if not user:

        update.message.reply_text(
            "😢 Анкет пока нет"
        )

        return

    last_profile[uid] = user[0]

    vip = "👑 VIP\n" if user[11] == 1 else ""

    username_text = ""

    if user[1]:
        username_text = f"\n👤 @{user[1]}\n"

    text = f"""
{vip}
❤️ {user[2]}, {user[3]}
🚻 {user[4]}
📍 {user[5]}
{username_text}
📝 {user[6]}

🎵 {user[7]}
✨ {user[8]}
🏷 {user[10]}
"""

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=user[9],
        caption=text,
        reply_markup=like_menu
    )

# =========================
# LIKE
# =========================

def like(update, context):

    uid = update.message.from_user.id

    if uid not in last_profile:
        return

    target = last_profile[uid]

    cursor.execute("""
    SELECT *
    FROM likes
    WHERE from_user=? AND to_user=?
    """, (uid, target))

    already = cursor.fetchone()

    if already:

        update.message.reply_text(
            "❤️ Ты уже лайкал эту анкету"
        )

        return

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
    SELECT *
    FROM likes
    WHERE from_user=? AND to_user=?
    """, (target, uid))

    match = cursor.fetchone()

    if match:

        update.message.reply_text(
            "💘 Взаимный лайк!"
        )

    else:

        update.message.reply_text(
            "❤️ Лайк отправлен"
        )

    show_profile(update, context)

# =========================
# VIEW LIKES
# =========================

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
            "😢 Тебя пока никто не лайкнул"
        )

        return

    target = likes[0][0]

    cursor.execute("""
    SELECT *
    FROM users
    WHERE user_id=?
    """, (target,))

    user = cursor.fetchone()

    if not user:
        return

    last_profile[uid] = target

    username_text = ""

    if user[1]:
        username_text = f"\n👤 @{user[1]}\n"

    text = f"""
👀 Тебя лайкнул(а):

❤️ {user[2]}, {user[3]}
🚻 {user[4]}
📍 {user[5]}
{username_text}
📝 {user[6]}

🎵 {user[7]}
✨ {user[8]}
🏷 {user[10]}
"""

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=user[9],
        caption=text,
        reply_markup=like_menu
    )

# =========================
# OTHER FUNCTIONS
# =========================

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
            "⭐ Избранное пусто"
        )

        return

    text = "⭐ Избранное:\n\n"

    for fav in favs:

        cursor.execute("""
        SELECT name, age, city
        FROM users
        WHERE user_id=?
        """, (fav[0],))

        user = cursor.fetchone()

        if user:

            text += f"❤️ {user[0]}, {user[1]} | 📍 {user[2]}\n"

    update.message.reply_text(text)

def my_profile(update, context):

    uid = update.message.from_user.id

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id=?
    """, (uid,))

    user = cursor.fetchone()

    if not user:
        return

    text = f"""
👤 Твоя анкета

❤️ {user[2]}, {user[3]}
📍 {user[5]}

📝 {user[6]}

🎵 {user[7]}
🏷 {user[10]}
"""

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=user[9],
        caption=text,
        reply_markup=menu
    )

def edit_profile(update, context):

    uid = update.message.from_user.id

    register_step[uid] = "name"
    temp_data[uid] = {}

    update.message.reply_text(
        "✏️ Введи новое имя"
    )

def delete_profile(update, context):

    uid = update.message.from_user.id

    cursor.execute("""
    DELETE FROM users
    WHERE user_id=?
    """, (uid,))

    conn.commit()

    update.message.reply_text(
        "🗑 Анкета удалена",
        reply_markup=menu
    )

def crush_day(update, context):

    show_profile(update, context)

def top_users(update, context):

    cursor.execute("""
    SELECT COUNT(*)
    FROM users
    """)

    users = cursor.fetchone()[0]

    update.message.reply_text(
        f"🏆 Пользователей в боте: {users}"
    )

def night_match(update, context):

    hour = datetime.datetime.now().hour

    if hour >= 23 or hour <= 5:

        update.message.reply_text(
            "🌙 Night Match активирован"
        )

        show_profile(update, context)

    else:

        update.message.reply_text(
            "🌙 Работает после 23:00"
        )

def music_vibe(update, context):

    update.message.reply_text(
        "🎵 Музыкальный вайб"
    )

    show_profile(update, context)

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

def help_command(update, context):

    update.message.reply_text(
        "💎 Apsny Love Premium\n\n"
        "❤️ Лайки\n"
        "💘 Матчи\n"
        "👀 Кто лайкнул\n"
        "⭐ Избранное\n"
        "🌙 Night Match\n"
        "🎵 Музыкальный вайб"
    )

def skip(update, context):
    show_profile(update, context)

# =========================
# START BOT
# =========================

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
