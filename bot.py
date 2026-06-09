from aiogram import Bot,Dispatcher,F
from aiogram.types import Message
from aiogram.filters import CommandStart
import asyncio,os
from audio_processor import make_hardtekk
TOKEN=os.getenv("BOT_TOKEN","PUT_TOKEN")
bot=Bot(TOKEN)
dp=Dispatcher()
@dp.message(CommandStart())
async def start(m:Message):
    await m.answer("Отправь аудио или музыку.")
@dp.message(F.audio|F.voice|F.document)
async def audio(m:Message):
    f=await bot.get_file((m.audio or m.voice or m.document).file_id)
    inp="temp/in.mp3";out="temp/out.mp3"
    await bot.download_file(f.file_path,inp)
    make_hardtekk(inp,out)
    await m.answer_audio(open(out,"rb"))
async def main():
    await dp.start_polling(bot)
if __name__=="__main__":
    asyncio.run(main())
