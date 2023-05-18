import os
from pathlib import Path
import openai
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from loguru import logger

from audio_file_operations import audio_convert, audio_recognition, FFmpeg
from main import bot
from main import dp
from states.talk_state import AI
from tts import TTS

tts = TTS()


# Изменить callback
@dp.callback_query_handler(text='back', state='*')
async def back(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[
                                  [InlineKeyboardButton(text="Поделись, пожалуйста, что тебя тревожит?", callback_data="start")]])
    await call.message.answer(
        f"Привет, я создан чтобы дать тебе ответы на интересующие тебя вопросы.",
        reply_markup=kb)
    await state.finish()


# pr_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
# stop_bt = types.KeyboardButton(text='Приостановить разговор', callback_data="stop")
# pr_kb.add(stop_bt)
#
#

# @dp.callback_query_handler(text='stop', state='*')
# async def stop_talk(call: types.CallbackQuery, state: FSMContext):
#     await state.finish()
#     kb_stop = types.ReplyKeyboardMarkup()
#     clear_talk = types.KeyboardButton(text='Стереть разговор', callback_data="clear")
#     continue_talk = types.KeyboardButton(text='Продолжить разговор', callback_data="continue")
#     kb_stop.add(clear_talk, continue_talk)
#     await call.message.answer('Разговор приостановлен', reply_markup=kb_stop)
#
#
# @dp.callback_query_handler(text='continue', state='*')
# async def clear(call: types.CallbackQuery, state: FSMContext):
#     await call.message.answer('Продолжение разговора')
#     await AI.talk.set()


@dp.callback_query_handler(text='clear', state='*')
async def clear(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('История общения стёрта')
    await state.update_data(history=[{"question": None, "answer": None}])


@dp.callback_query_handler(text='start')
async def chat_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Поделись, пожалуйста, что тебя тревожит?")
    # await Type_answer.speech.set()
    await AI.talk.set()
    await state.update_data(history=[{"question": None, "answer": None}], variable=False)


keyboard = types.InlineKeyboardMarkup()
keyboard.add(types.InlineKeyboardButton(text="Текстовое сообщение", callback_data="text"),
             types.InlineKeyboardButton(text="Голосовое сообщение", callback_data="voice"),
             types.InlineKeyboardButton(text="Голосовое и текстовое сообщение", callback_data="both"))


async def ask_type_of_message(message: types.Message):
    await message.answer_chat_action("typing")
    await message.answer("Выберите тип сообщения:", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data in ["text", "voice", "both"], state=AI.type_answer)
async def process_callback_data(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    await state.update_data(message_type=data)
    await bot.answer_callback_query(callback_query.id)
    user_data = await state.get_data()
    resp_ai = user_data.get("resp_ai")
    message_type = user_data.get("message_type")
    if message_type == "voice":
        await callback_query.message.answer_chat_action("record_voice")
        out_filename = tts.text_to_ogg(resp_ai)
        path = Path("", out_filename)
        voice = InputFile(path)
        await bot.send_voice(callback_query.from_user.id, voice)
        os.remove(out_filename)  # delete temporary file
    elif message_type == "text":
        await callback_query.message.answer_chat_action("typing")
        await callback_query.message.answer(resp_ai)
    else:
        await callback_query.message.answer_chat_action("typing")
        await callback_query.message.answer(resp_ai)
        await callback_query.message.answer_chat_action("record_voice")
        out_filename = tts.text_to_ogg(resp_ai)
        path = Path("", out_filename)
        voice = InputFile(path)
        await bot.send_voice(callback_query.from_user.id, voice)
        os.remove(out_filename)  # delete temporary file

    # Переход в режим ожидания
    # await callback_query.message.answer()
    # await AI.wait.set() - ожидание, без действий, можно поменять тип ответа
    await AI.talk.set()


# Обработка ответа GPT AI
async def ai_resp(data, text, message):
    await message.answer_chat_action("typing")
    history = []
    if len(data) > 1:
        for index in range(0, len(data)):
            if data[index].get('question') is None:
                data[index]['question'] = text
                d = {"role": "user", "content": data[index]['question']}
                history.append(d)
            else:
                d = [{"role": "system",
                  "content": "Вы - психолог, к которому пришел пациент, вы должны дать ему подробный ответ, что можно сделать в случае его проблемы"},
                 {"role": "user",
                  "content": "ответь в режиме психолога, но не советуй обращаться к специалисту и не говори, что не можешь заменить его:" +
                             data[index]['question']},
                 {"role": "assistant", "content": data[index].get('answer')}]
                history += d
    else:
        data[0]['question'] = text
        d = {"role": "user",
         "content": "Перейди в режим психолога и сформулируй вопрос для психологической консультации из следующего, но не советуй посетить специалиста, а попробуй разобраться сам: " +
                    data[0].get(
                        'question') + " Твой вопрос должен начинаться с 'Правильно ли я понимаю', а дальше твои рассуждения, в каком психологическом аспекте необходимо помочь пользователю"}

        history.append(d)
    print(history)
    request = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history,
        max_tokens=1500,
        temperature=1,
    )
    resp_ai = request['choices'][0]['message']['content']
    return resp_ai


# Обработка текстового сообщения
@dp.message_handler(state=AI.talk)
async def chat_talk(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = data.get('history')
    text = message.text
    resp_ai = await ai_resp(data, text, message)
    data[-1]['answer'] = resp_ai.replace('\n', '')
    text = f"{message.from_user.username}\nQ:{data[-1]['question']}\nA:{data[-1]['answer']}"
    data.append({"question": None, "answer": None})
    if len(data) > 25:
        await state.update_data(history=[{"question": None, "answer": None}])
    await state.update_data(history=data)
    await state.update_data(resp_ai=resp_ai)
    await AI.type_answer.set()
    await ask_type_of_message(message)


# Перевод аудио в текст Speech to Text (STT) - Хэндлер на получение голосового и аудио сообщения
@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.AUDIO], state=AI.talk)
async def voice_message_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer_chat_action("typing")
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    logger.info(file_path)
    await bot.download_file(file_path, FFmpeg.FILE_IN)
    await audio_convert()
    text = await audio_recognition()
    if not text:
        text = "Формат документа не поддерживается"
    #############################################################
    data = await state.get_data()
    data = data.get('history')
    resp_ai = await ai_resp(data, text, message)
    data[-1]['answer'] = resp_ai.replace('\n', '')
    text = f"{message.from_user.username}\nQ:{data[-1]['question']}\nA:{data[-1]['answer']}"
    data.append({"question": None, "answer": None})
    if len(data) > 20:
        await state.update_data(history=[{"question": None, "answer": None}])
    await state.update_data(history=data)
    await state.update_data(resp_ai=resp_ai)
    await AI.type_answer.set()
    await ask_type_of_message(message)


def register_handlers_AI(dp: Dispatcher):
    # dp.register_message_handler(stop_talk, text=['stop'])
    dp.register_message_handler(chat_start, text=['start'])
    dp.register_message_handler(chat_talk, state=AI.talk)
    dp.register_message_handler(back, text=['back'])
    dp.register_message_handler(clear, text=['clear'])
