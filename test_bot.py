import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=['photo', 'video', 'animation', 'voice', 'audio'])
async def get_file_id(message: types.Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "фото"
    elif message.video:
        file_id = message.video.file_id
        file_type = "видео"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "GIF"
    elif message.voice:
        file_id = message.voice.file_id
        file_type = "голосовое"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "аудио"
    else:
        return
    await message.reply(f"✅ {file_type} file_id:\n`{file_id}`")

@dp.message_handler()
async def echo(message: types.Message):
    await message.reply("Я понимаю только медиафайлы для получения file_id.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)