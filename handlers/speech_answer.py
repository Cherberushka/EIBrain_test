from keyboards import *
from aiogram import Dispatcher, types


speech_answer_flag = False


# from bot import dp
async def send_welcome(message: types.Message):
    username = message.from_user.username
    await message.reply("Режим озвучивания ответа",
                        reply_markup=keyboard_speech_answer)


# @dp.callback_query_handler(text='on_sa')
async def on_speech_answer(callback: types.CallbackQuery):
    speech_answer_flag = True
    await callback.message.answer("Озвучка ответов включена")
    await callback.answer()


# @dp.callback_query_handler(text='off_sa')
async def off_speech_answer(callback: types.CallbackQuery):
    speech_answer_flag = False
    await callback.message.answer("Озвучка ответов выключена")
    await callback.answer()


def register_handlers_speech_answer(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['speech_answer'])
    dp.register_callback_query_handler(on_speech_answer, text='on_sa')
    dp.register_callback_query_handler(off_speech_answer, text='off_sa')
