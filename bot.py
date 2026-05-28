import sqlite3
import random
import os

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

conn = sqlite3.connect("dating.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
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
    keyboard=[
        [KeyboardButton("🔍 Смотреть анкеты")]
    ],
    resize_keyboard=True
)

register_step = {}
temp_data = {}
last_profile = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    register_step[uid] = "name"
    temp_data[uid] = {}

    await update.message.reply_text(
        "❤️ Добро пожаловать\n\nКак тебя зовут?"
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if text == "🔍 Смотреть анкеты":
        await show_profile(update, context)
        return

    if text == "❤️":
        await like(update, context)
        return

    if text == "👎":
        await skip(update, context)
        return

    if uid not in register_step:
        return

    step = register_step[uid]

    if step == "name":
        temp_data[uid]["name"] = text
        register_step[uid] = "age"

        await update.message.reply_text(
            "Сколько тебе лет?"
        )

    elif step == "age":
        temp_data[uid]["age"] = text
        register_step[uid] = "city"

        await update.message.reply_text(
            "Из какого ты города?"
        )

    elif step == "city":
        temp_data[uid]["city"] = text
        register_step[uid] = "bio"

        await update.message.reply_text(
            "Напиши описание о себе"
        )

    elif step == "bio":
        temp_data[uid]["bio"] = text
        register_step[uid] = "photo"

        await update.message.reply_text(
            "Теперь отправь фото 📸"
        )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if uid not in register_step:
        return

    if register_step[uid] != "photo":
        return

    photo = update.message.photo[-1].file_id

    data = temp_data[uid]

    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        uid,
        data["name"],
        data["age"],
        data["city"],
        data["bio"],
        photo
    ))

    conn.commit()

    del register_step[uid]

    await update.message.reply_text(
        "✅ Анкета сохранена",
        reply_markup=menu
    )

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id != ?
    """, (uid,))

    users = cursor.fetchall()

    if not users:
        await update.message.reply_text(
            "Анкет пока нет"
        )
        return

    target = random.choice(users)

    last_profile[uid] = target[0]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("❤️"), KeyboardButton("👎")]
        ],
        resize_keyboard=True
    )

    text = f"""
❤️ {target[1]}, {target[2]}
📍 {target[3]}

{target[4]}
"""

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=target[5],
        caption=text,
        reply_markup=keyboard
    )

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(
            "🎉 У вас взаимная симпатия!"
        )

    else:
        await update.message.reply_text(
            "❤️ Лайк отправлен"
        )

    await show_profile(update, context)

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_profile(update, context)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    )
)

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        photo_handler
    )
)

print("BOT STARTED")

app.run_polling()
