from aiogram import executor

from main import dp
from handlers import *
from utils.set_bot_commands import set_default_commands

AI.register_handlers_AI(dp)
start.register_handlers_start(dp)
help.register_handlers_help(dp)
# speech_answer.register_handlers_speech_answer(dp)
# speech_answer_flag = False


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
