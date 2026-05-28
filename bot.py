import sqlite3
import random
import os

from telegram import ReplyKeyboardMarkup
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
    profile TEXT
)
""")

conn.commit()

menu = ReplyKeyboardMarkup(
    [["🔍 Смотреть анкеты"]],
    resize_keyboard=True
)

def start(update, context):
    update.message.reply_text(
        "❤️ Добро пожаловать\n\n"
        "Отправь анкету одним сообщением\n\n"
        "Пример:\n"
        "Аслан, 22, Сухум",
        reply_markup=menu
    )

def message(update, context):
    text = update.message.text
    uid = update.message.from_user.id

    if text == "🔍 Смотреть анкеты":

        cursor.execute("""
        SELECT * FROM users
        WHERE user_id != ?
        """, (uid,))

        users = cursor.fetchall()

        if not users:
            update.message.reply_text("Анкет пока нет")
            return

        target = random.choice(users)

        update.message.reply_text(
            f"❤️ Анкета:\n\n{target[1]}"
        )

        return

    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?)
    """, (uid, text))

    conn.commit()

    update.message.reply_text(
        "✅ Анкета сохранена",
        reply_markup=menu
    )

print("BOT STARTED")

updater = Updater(TOKEN, use_context=True)

dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))

dp.add_handler(
    MessageHandler(
        Filters.text,
        message
    )
)

updater.start_polling()
updater.idle()
