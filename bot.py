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

# USERS
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
    photo TEXT
)
""")

# LIKES
cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
    from_user INTEGER,
    to_user INTEGER
)
""")

# FAVORITES
cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER,
    favorite_id INTEGER
)
""")

conn.commit()

# MAIN MENU
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

# LIKE MENU
like_menu = ReplyKeyboardMarkup(
    [
        ["❤️", "👎"],
        ["⭐ В избранное"],
        ["🏠 Главное меню"]
    ],
    resize_keyboard=True
)

register_step = {}
temp_data = {}
last_profile = {}

# START
def start(update, context):

    uid = update.message.from_user.id

    register_step[uid] = "name"
    temp_data[uid] = {}

    update.message.reply_text(
        "❤️ Добро пожаловать в Apsny Love\n\n"
        "Как тебя зовут?"
    )

# TEXT HANDLER
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

    # MOOD SAVE
    if text in moods:

        temp_data.setdefault(uid, {})
        temp_data[uid]["mood"] = text

        update.message.reply_text(
            f"✨ Настроение установлено:\n\n{text}",
            reply_markup=menu
        )

        return

    # MENU
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
        mood_menu(update, context)
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
            "Из какого ты города?"
        )

    elif step == "city":

        temp_data[uid]["city"] = text
        register_step[uid] = "bio"

        update.message.reply_text(
            "Напиши описание о себе"
        )

    elif step == "bio":

        temp_data[uid]["bio"] = text
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

# PHOTO
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

        mood = data.get("mood", "🌊 Без настроения")

        cursor.execute("""
        INSERT OR REPLACE INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            photo
        ))

        conn.commit()

        del register_step[uid]

        update.message.reply_text(
            "✅ Анкета сохранена",
            reply_markup=menu
        )

    except Exception as e:
        print(e)

# SHOW PROFILE
def show_profile(update, context):

    uid = update.message.from_user.id

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id != ?
    """, (uid,))

    users = cursor.fetchall()

    if not users:

        update.message.reply_text(
            "Анкет пока нет"
        )

        return

    target = random.choice(users)

    last_profile[uid] = target[0]

    text = f"""
❤️ {target[2]}, {target[3]}
🚻 {target[4]}
📍 {target[5]}

📝 {target[6]}

🎵 {target[7]}
✨ {target[8]}
"""

    try:

        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=target[9],
            caption=text,
            reply_markup=like_menu
        )

    except Exception as e:
        print(e)

# LIKE
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

    # SEND LIKE
    try:

        context.bot.send_message(
            chat_id=target,
            text="❤️ Кто-то лайкнул твою анкету"
        )

    except:
        pass

    # MATCH CHECK
    cursor.execute("""
    SELECT * FROM likes
    WHERE from_user=? AND to_user=?
    """, (target, uid))

    match = cursor.fetchone()

    if match:

        cursor.execute("""
        SELECT username FROM users
        WHERE user_id=?
        """, (target,))

        user = cursor.fetchone()

        username = user[0]

        if username:

            update.message.reply_text(
                f"🎉 Взаимная симпатия!\n\n@{username}"
            )

            try:

                context.bot.send_message(
                    chat_id=target,
                    text=f"🎉 Взаимная симпатия!\n\n@{update.message.from_user.username}"
                )

            except:
                pass

        else:

            update.message.reply_text(
                "🎉 Взаимная симпатия!"
            )

    else:

        update.message.reply_text(
            "❤️ Лайк отправлен"
        )

    show_profile(update, context)

# SKIP
def skip(update, context):
    show_profile(update, context)

# FAVORITES
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

# FAVORITES LIST
def favorites(update, context):

    uid = update.message.from_user.id

    cursor.execute("""
    SELECT favorite_id FROM favorites
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

# PROFILE
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

    text = f"""
👤 Твоя анкета

❤️ {user[2]}, {user[3]}
🚻 {user[4]}
📍 {user[5]}

📝 {user[6]}

🎵 {user[7]}
✨ {user[8]}
"""

    try:

        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=user[9],
            caption=text,
            reply_markup=menu
        )

    except:
        pass

# DELETE
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

# EDIT
def edit_profile(update, context):

    uid = update.message.from_user.id

    register_step[uid] = "name"
    temp_data[uid] = {}

    update.message.reply_text(
        "✏️ Введи новое имя"
    )

# MOOD MENU
def mood_menu(update, context):

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

    update.message.reply_text(
        "✨ Выбери настроение",
        reply_markup=mood_keyboard
    )

# CRUSH DAY
def crush_day(update, context):

    cursor.execute("""
    SELECT * FROM users
    ORDER BY RANDOM()
    LIMIT 1
    """)

    user = cursor.fetchone()

    if not user:

        update.message.reply_text(
            "Нет анкет"
        )

        return

    text = f"""
💘 Crush дня

❤️ {user[2]}, {user[3]}
📍 {user[5]}

🎵 {user[7]}
✨ {user[8]}
"""

    try:

        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=user[9],
            caption=text,
            reply_markup=menu
        )

    except:
        pass

# NIGHT MATCH
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

# MUSIC VIBE
def music_vibe(update, context):

    cursor.execute("""
    SELECT * FROM users
    ORDER BY RANDOM()
    LIMIT 1
    """)

    user = cursor.fetchone()

    if not user:
        return

    text = f"""
🎵 Музыкальный вайб

❤️ {user[2]}
🎧 Любит: {user[7]}

✨ {user[8]}
"""

    try:

        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=user[9],
            caption=text,
            reply_markup=like_menu
        )

    except:
        pass

# HELP
def help_command(update, context):

    update.message.reply_text(
        "ℹ️ Apsny Love\n\n"
        "❤️ Лайки\n"
        "💘 Матчи\n"
        "🌙 Night Match\n"
        "🎵 Музыкальный вайб\n"
        "⭐ Избранное\n"
        "🌊 Настроение"
    )

# STATS
def stats(update, context):

    cursor.execute("""
    SELECT COUNT(*) FROM users
    """)

    users = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM likes
    """)

    likes = cursor.fetchone()[0]

    update.message.reply_text(
        f"📊 Статистика\n\n"
        f"👤 Пользователей: {users}\n"
        f"❤️ Лайков: {likes}"
    )

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
