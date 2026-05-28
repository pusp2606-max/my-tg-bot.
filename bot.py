import os
import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler

# Этапы регистрации
BIO, PHOTO, REGION, INTERESTS = range(4)

# --- Главное меню ---
def main_menu():
    keyboard = [
        [KeyboardButton("📇 Мой профиль"), KeyboardButton("🔎 Поиск")],
        [KeyboardButton("⚙️ Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Создание базы SQLite ---
async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            name TEXT,
            bio TEXT,
            photo TEXT,
            region TEXT,
            interests TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS likes(
            user_id INTEGER,
            liked_id INTEGER
        )
        """)
        await db.commit()

# --- Старт ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            if not await cursor.fetchone():
                await db.execute("INSERT INTO users(id, name) VALUES(?, ?)", (user_id, name))
                await db.commit()
    await update.message.reply_text(
        "Привет! Это Abkhazia Dating Bot ❤️\n"
        "Используй /setprofile чтобы создать профиль.",
        reply_markup=main_menu()
    )

# --- Начало регистрации ---
async def setprofile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши коротко о себе (био):")
    return BIO

async def bio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET bio=? WHERE id=?", (text, user_id))
        await db.commit()
    await update.message.reply_text("Отлично! Пришли фото для профиля.")
    return PHOTO

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo_file = update.message.photo[-1].file_id
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET photo=? WHERE id=?", (photo_file, user_id))
        await db.commit()
    await update.message.reply_text("Фото сохранено! Напиши свой регион:")
    return REGION

async def region_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    region = update.message.text.strip()
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET region=? WHERE id=?", (region, user_id))
        await db.commit()
    await update.message.reply_text("Теперь напиши свои интересы через запятую:")
    return INTERESTS

async def interests_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    interests = ",".join([i.strip().lower() for i in update.message.text.split(",")])
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET interests=? WHERE id=?", (interests, user_id))
        await db.commit()
    await update.message.reply_text("Профиль создан! Используй 🔎 Поиск для поиска других пользователей.", reply_markup=main_menu())
    return ConversationHandler.END

# --- Просмотр профилей ---
async def browse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    async with aiosqlite.connect("bot.db") as db:
        # Получаем мой регион и интересы
        async with db.execute("SELECT region, interests FROM users WHERE id=?", (user_id,)) as cursor:
            me = await cursor.fetchone()
        region, my_interests = me
        my_interests_set = set(my_interests.split(",")) if my_interests else set()
        # Находим пользователей в том же регионе
        async with db.execute("SELECT id, name, bio, photo, interests FROM users WHERE id != ? AND region=?", (user_id, region)) as cursor:
            async for row in cursor:
                uid, name, bio, photo, interests = row
                interests_set = set(interests.split(",")) if interests else set()
                common = my_interests_set & interests_set
                caption = f"{name}\n{bio}\nИнтересы: {interests}"
                if common:
                    caption += f"\nСовпадения: {', '.join(common)}"
                keyboard = [
                    [
                        InlineKeyboardButton("❤️ Лайк", callback_data=f"like_{uid}"),
                        InlineKeyboardButton("❌ Дизлайк", callback_data=f"dislike_{uid}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if photo:
                    await update.message.reply_photo(photo=photo, caption=caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(caption, reply_markup=reply_markup)
                return
        await update.message.reply_text("Нет доступных пользователей в твоём регионе.")

# --- Обработка лайков ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    async with aiosqlite.connect("bot.db") as db:
        if data.startswith("like_"):
            liked_id = int(data.split("_")[1])
            await db.execute("INSERT INTO likes(user_id, liked_id) VALUES(?, ?)", (user_id, liked_id))
            await db.commit()
            # Проверка взаимного лайка
            async with db.execute("SELECT * FROM likes WHERE user_id=? AND liked_id=?", (liked_id, user_id)) as cursor:
                if await cursor.fetchone():
                    await query.edit_message_text("Взаимная симпатия! 🎉 Напиши друг другу в личку.")
                else:
                    await query.edit_message_text("Вы лайкнули пользователя!")
        elif data.startswith("dislike_"):
            await query.edit_message_text("Вы пропустили пользователя.")

# --- Главное меню ---
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    async with aiosqlite.connect("bot.db") as db:
        if text == "📇 Мой профиль":
            async with db.execute("SELECT name, bio, photo, region, interests FROM users WHERE id=?", (user_id,)) as cursor:
                user = await cursor.fetchone()
                name, bio, photo, region, interests = user
                text = f"{name}\n{bio}\nРегион: {region}\nИнтересы: {interests}"
                if photo:
                    await update.message.reply_photo(photo=photo, caption=text)
                else:
                    await update.message.reply_text(text)
        elif text == "🔎 Поиск":
            await browse(update, context)
        elif text == "⚙️ Настройки":
            await update.message.reply_text("Пока здесь ничего нет, но скоро добавим настройки!")

# --- Основная функция ---
async def main():
    await init_db()
    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('setprofile', setprofile)],
        states={
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio_handler)],
            PHOTO: [MessageHandler(filters.PHOTO, photo_handler)],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region_handler)],
            INTERESTS: [MessageHandler(filters.TEXT
