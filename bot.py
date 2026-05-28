import sqlite3
import random
import os

from telegram import (
    ReplyKeyboardMarkup
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters
)

TOKEN = os.getenv("BOT_TOKEN")

conn = sqlite3.connect("dating.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    name TEXT,
    age TEXT,
    city TEXT,
    bio TEXT,
    photo TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
    from_user INTEGER,
    to_user INTEGER
)
""")

conn.commit()

menu = ReplyKeyboardMarkup(
    [["🔍 Смотреть анкеты"]],
    resize_keyboard=True
)

like_menu = ReplyKeyboardMarkup(
    [["❤️", "👎"]],
    resize_keyboard=True
)

register_step = {}
temp_data = {}
last_profile = {}

def start(update, context):
    uid = update.message.from_user.id

    register_step[uid] = "name"
    temp_data[uid] = {}

    update.message.reply_text(
        "❤️ Добро пожаловать в LoveBot Абхазия\n\n"
        "Как тебя зовут?"
    )

def text_handler(update, context):
    uid = update.message.from_user.id
    text = update.message.text

    if text == "🔍 Смотреть анкеты":
        show_profile(update, context)
        return

    if text == "❤️":
        like(update, context)
        return

    if text == "👎":
        skip(update, context)
        return

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
        register_step[uid] = "photo"

        update.message.reply_text(
            "Теперь отправь фото 📸"
        )

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

        cursor.execute("""
        INSERT OR REPLACE INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            uid,
            username,
            data["name"],
            data["age"],
            data["city"],
            data["bio"],
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
📍 {target[4]}

{target[5]}
"""

    try:
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=target[6],
            caption=text,
            reply_markup=like_menu
        )

    except:
        pass

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

        else:
            update.message.reply_text(
                "🎉 Взаимная симпатия!"
            )

    else:
        update.message.reply_text(
            "❤️ Лайк отправлен"
        )

    show_profile(update, context)

def skip(update, context):
    show_profile(update, context)

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
