from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.builtin import CommandHelp

from main import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")

    await message.answer("\n".join(text))


def register_handlers_help(dp: Dispatcher):
    dp.register_message_handler(bot_help, commands=['help'])
