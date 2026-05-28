import os
import asyncio
import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)

# Этапы
BIO, PHOTO, REGION, INTERESTS = range(4)

def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📇 Мой профиль"), KeyboardButton("🔎 Поиск")],
        [KeyboardButton("⚙️ Настройки")]
    ], resize_keyboard=True)

async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, bio TEXT, photo TEXT, region TEXT, interests TEXT)")
        await db.execute("CREATE TABLE IF NOT EXISTS likes (user_id INTEGER, liked_id INTEGER)")
        await db.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT id FROM users WHERE id = ?", (user_id,)) as cursor:
            if not await cursor.fetchone():
                await db.execute("INSERT INTO users(id, name) VALUES(?, ?)", (user_id, name))
                await db.commit()
    await update.message.reply_text("Привет! Это Abkhazia Dating Bot ❤️\nИспользуй /setprofile для создания профиля.", reply_markup=main_menu())

async def setprofile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши коротко о себе (био):")
    return BIO

async def bio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET bio=? WHERE id=?", (update.message.text, update.effective_user.id))
        await db.commit()
    await update.message.reply_text("Отлично! Пришли фото для профиля.")
    return PHOTO

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправь именно фото.")
        return PHOTO
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET photo=? WHERE id=?", (update.message.photo[-1].file_id, update.effective_user.id))
        await db.commit()
    await update.message.reply_text("Фото сохранено! Напиши свой регион:")
    return REGION

async def region_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET region=? WHERE id=?", (update.message.text.strip(), update.effective_user.id))
        await db.commit()
    await update.message.reply_text("Напиши свои интересы через запятую:")
    return INTERESTS

async def interests_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    interests = ",".join([i.strip().lower() for i in update.message.text.split(",")])
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET interests=? WHERE id=?", (interests, update.effective_user.id))
        await db.commit()
    await update.message.reply_text("Профиль создан! Используй 🔎 Поиск.", reply_markup=main_menu())
    return ConversationHandler.END

async def browse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT region, interests FROM users WHERE id=?", (user_id,)) as cursor:
            me = await cursor.fetchone()
        if not me:
            await update.message.reply_text("Сначала /setprofile")
            return
        
        async with db.execute("SELECT id, name, bio, photo, interests FROM users WHERE id != ? AND region=?", (user_id, me[0])) as cursor:
            async for row in cursor:
                uid, name, bio, photo, interests = row
                keyboard = [[InlineKeyboardButton("❤️ Лайк", callback_data=f"like_{uid}"), InlineKeyboardButton("❌ Дизлайк", callback_data=f"dislike_{uid}")]]
                if photo:
                    await update.message.reply_photo(photo=photo, caption=f"{name}\n{bio}\nИнтересы: {interests}", reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    await update.message.reply_text(f"{name}\n{bio}", reply_markup=InlineKeyboardMarkup(keyboard))
                return
    await update.message.reply_text("Пока нет новых анкет в твоем регионе.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if data.startswith("like_"):
        liked_id = int(data.split("_")[1])
        async with aiosqlite.connect("bot.db") as db:
            await db.execute("INSERT INTO likes(user_id, liked_id) VALUES(?, ?)", (user_id, liked_id))
            await db.commit()
        await query.edit_message_text("Лайк отправлен!")
    elif data.startswith("dislike_"):
        await query.edit_message_text("Пропущено.")

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔎 Поиск":
        await browse(update, context)
    elif update.message.text == "📇 Мой профиль":
        await update.message.reply_text("Функция профиля в разработке.")

async def main():
    await init_db()
    token = os.environ.get("BOT_TOKEN")
    if not token:
        return
    app = ApplicationBuilder().token(token).build()
    
    conv = ConversationHandler(entry_points=[CommandHandler("setprofile", setprofile)], 
                               states={BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio_handler)],
                                       PHOTO: [MessageHandler(filters.PHOTO, photo_handler)],
                                       REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region_handler)],
                                       INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, interests_handler)]},
                               fallbacks=[])
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Ждем сигнала остановки
    stop_signal = asyncio.Event()
    await stop_signal.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
