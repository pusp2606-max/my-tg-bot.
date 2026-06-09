import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize
import os

# Твой токен от BotFather
TOKEN = "8851735547:AAFGzJFkAMnKFHud3i8lMV9gxN6AqeofGlA"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def process_hardtekk(input_path: str, output_path: str):
    """Ядро обработки Hardtekk."""
    audio = AudioSegment.from_file(input_path)
    samples = np.array(audio.get_array_of_samples())
    
    # Жесткий клиппинг (агрессивный звук)
    max_val = np.iinfo(samples.dtype).max
    threshold = max_val * 0.8  # Порог среза
    samples = np.clip(samples, -threshold, threshold)
    
    audio = audio._spawn(samples.tobytes())
    audio = normalize(audio + 6.0) # Буст громкости
    audio.export(output_path, format="wav")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Пришли мне аудиофайл, и я сделаю из него Hardtekk.")

@dp.message(F.audio | F.voice)
async def handle_audio(message: types.Message):
    # Получаем файл из сообщения
    file_id = message.audio.file_id if message.audio else message.voice.file_id
    file = await bot.get_file(file_id)
    
    input_filename = f"input_{file_id}.ogg"
    output_filename = f"hardtekk_{file_id}.wav"
    
    await bot.download_file(file.file_path, input_filename)
    await message.answer("Обрабатываю звук в стиле Hardtekk...")
    
    # Обработка
    process_hardtekk(input_filename, output_filename)
    
    # Отправка результата
    await message.reply_audio(audio=FSInputFile(output_filename), caption="Твой Hardtekk готов!")
    
    # Удаление временных файлов
    os.remove(input_filename)
    os.remove(output_filename)

if __name__ == "__main__":
    print("Бот запущен...")
    dp.run_polling(bot)
