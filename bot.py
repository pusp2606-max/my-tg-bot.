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
        ["👤 Моя анкета", "❤️ Избранное"],
        ["✏️ Изменить анкету"],
        ["🗑 Удалить анкету"],
        ["ℹ️ Помощь", "📊 Статистика"]
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
        "❤️ Добро пожаловать в LoveBot Абхазия\n\n"
        "Как тебя зовут?"
    )

# TEXT HANDLER
def text_handler(update, context):
    uid = update.message.from_user.id
    text = update.message.text

    # MENU
    if text == "🔍 Смотреть анкеты":
        show_profile(update, context)
        return

    if text == "👤 Моя анкета":
        my_profile(update, context)
        return

    if text == "🗑 Удалить анкету":
        delete_profile(update, context)
        return

    if text == "✏️ Изменить анкету":
        edit_profile(update, context)
        return

    if text == "❤️ Избранное":
        favorites(update, context)
        return

    if text == "📊 Статистика":
        stats(update, context)
        return

    if text == "ℹ️ Помощь":
        help_command(update, context)
        return

    if text == "🏠 Главное меню":
        update.message.reply_text(
            "Главное меню",
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
            "Твой пол?\n\n"
            "Напиши:\n"
            "М\nили\nЖ"
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

        cursor.execute("""
        INSERT OR REPLACE INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uid,
            username,
            data["name"],
            data["age"],
            data["gender"],
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

{target[6]}
"""

    try:
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=target[7],
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

# SKIP
def skip(update, context):
    show_profile(update, context)

# FAVORITE
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
            "Избранное пусто"
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

# MY PROFILE
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

{user[6]}
"""

    try:
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=user[7],
            caption=text,
            reply_markup=menu
        )

    except Exception as e:
        print(e)

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

# HELP
def help_command(update, context):
    update.message.reply_text(
        "ℹ️ Команды:\n\n"
        "🔍 Смотреть анкеты\n"
        "👤 Моя анкета\n"
        "❤️ Избранное\n"
        "✏️ Изменить анкету\n"
        "🗑 Удалить анкету"
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
