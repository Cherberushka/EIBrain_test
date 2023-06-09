from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.builtin import CommandStart

from main import dp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[[InlineKeyboardButton(text="Начать чат с ИИ", callback_data="start")]])
    await message.answer(
        f"Привет, {message.from_user.full_name}!",
        reply_markup=kb)


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=['start'])
