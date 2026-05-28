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
    profile TEXT
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

last_view = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Добро пожаловать в LoveBot Абхазия\n\n"
        "Отправь анкету одним сообщением\n\n"
        "Пример:\n"
        "Аслан, 22, Сухум\nЛюблю море и спорт"
    )

async def save_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.message.from_user.id

    if text == "🔍 Смотреть анкеты":
        await show_profile(update)
        return

    if text == "❤️":
        await like_profile(update)
        return

    if text == "👎":
        await skip_profile(update)
        return

    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?)
    """, (uid, text))

    conn.commit()

    await update.message.reply_text(
        "✅ Анкета сохранена",
        reply_markup=menu
    )

async def show_profile(update):
    uid = update.message.from_user.id

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id != ?
    """, (uid,))

    users = cursor.fetchall()

    if not users:
        await update.message.reply_text("Анкет пока нет")
        return

    target = random.choice(users)

    last_view[uid] = target[0]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("❤️"), KeyboardButton("👎")]
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        f"❤️ Анкета:\n\n{target[1]}",
        reply_markup=keyboard
    )

async def like_profile(update):
    uid = update.message.from_user.id

    if uid not in last_view:
        return

    target = last_view[uid]

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
            "🎉 Взаимная симпатия!"
        )

    else:
        await update.message.reply_text(
            "❤️ Лайк отправлен"
        )

    await show_profile(update)

async def skip_profile(update):
    await show_profile(update)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        save_profile
    )
)

print("BOT STARTED")

app.run_polling()
