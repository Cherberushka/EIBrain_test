import os
from pathlib import Path

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from audio_file_operations import audio_convert, audio_recognition, FFmpeg
from tts import TTS
from loguru import logger

from main import dp
from states.talk_state import AI
import openai
from main import bot

tts = TTS()


@dp.callback_query_handler(text='start')
async def chat_start(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Закончить чат", callback_data="start"),
         InlineKeyboardButton(text="Стереть память", callback_data="start")]])

    await call.message.answer("Отправть сообщение, чтобы начать переписку", reply_markup=kb)
    await AI.talk.set()
    await state.update_data(history=[{"question": None, "answer": None}])


@dp.message_handler(state=AI.talk)
async def chat_talk(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = data.get('history')
    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Закончить чат", callback_data="back"),
         InlineKeyboardButton(text="Стереть память", callback_data="clear")]])
    await message.answer("Генерация ответа...", reply_markup=kb)

    history = []
    if len(data) > 1:
        for index in range(0, len(data)):
            if data[index].get('question') is None:
                data[index]['question'] = message.text
                d = {"role": "user", "content": data[index]['question']}
                history.append(d)
            else:
                d = [{"role": "user", "content": data[index]['question']},
                     {"role": "assistant", "content": data[index].get('answer')}]
                history += d
    else:
        data[0]['question'] = message.text
        d = {"role": "user", "content": data[0].get('question')}
        history.append(d)
    print(history)
    request = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history,
        max_tokens=1500,
        temperature=1,
    )
    resp_ai = request['choices'][0]['message']['content']
    data[-1]['answer'] = resp_ai.replace('\n', '')
    text = f"{message.from_user.username}\nQ:{data[-1]['question']}\nA:{data[-1]['answer']}"
    data.append({"question": None, "answer": None})
    if len(data) > 10:
        await state.update_data(history=[{"question": None, "answer": None}])
    await state.update_data(history=data)
    await message.answer(resp_ai)

    # Отправка голосового сообщения
    out_filename = tts.text_to_ogg(resp_ai)
    path = Path("", out_filename)
    voice = InputFile(path)
    await bot.send_voice(message.from_user.id, voice)

    # Удаление временного файла
    os.remove(out_filename)


# Перевод аудио в текст Speech to Text (STT)
# Хэндлер на получение голосового и аудио сообщения
@dp.message_handler(content_types=[types.ContentType.VOICE,
                                   types.ContentType.AUDIO],
                    state=AI.talk)
async def voice_message_handler(message: types.Message, state: FSMContext) -> None:
    """handle audio from user, transcribe and dend text answer"""
    # if message.content_type == types.ContentType.VOICE:
    #     file_id = message.voice.file_id
    # elif message.content_type == types.ContentType.AUDIO:
    #     file_id = message.audio.file_id
    # else:
    #     await message.reply("Формат документа не поддерживается")
    #     return
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
    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Закончить чат", callback_data="back"),
         InlineKeyboardButton(text="Стереть память", callback_data="clear")]])
    await message.answer("Генерация ответа...", reply_markup=kb)

    history = []
    if len(data) > 1:
        for index in range(0, len(data)):
            if data[index].get('question') is None:
                data[index]['question'] = text
                d = {"role": "user", "content": data[index]['question']}
                history.append(d)
            else:
                d = [{"role": "user", "content": data[index]['question']},
                     {"role": "assistant", "content": data[index].get('answer')}]
                history += d
    else:
        data[0]['question'] = text
        d = {"role": "user", "content": data[0].get('question')}
        history.append(d)
    print(history)
    request = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history,
        max_tokens=1500,
        temperature=1,
    )
    resp_ai = request['choices'][0]['message']['content']
    data[-1]['answer'] = resp_ai.replace('\n', '')
    text = f"{message.from_user.username}\nQ:{data[-1]['question']}\nA:{data[-1]['answer']}"
    data.append({"question": None, "answer": None})
    if len(data) > 10:
        await state.update_data(history=[{"question": None, "answer": None}])
    await state.update_data(history=data)
    await message.answer(resp_ai)

    # Отправка голосового сообщения
    out_filename = tts.text_to_ogg(resp_ai)
    path = Path("", out_filename)
    voice = InputFile(path)
    await bot.send_voice(message.from_user.id, voice)

    # Удаление временного файла
    os.remove(out_filename)


@dp.callback_query_handler(text='back', state='*')
async def back(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[[InlineKeyboardButton(text="Начать чат с ИИ", callback_data="start")]])
    await call.message.answer(
        f"Привет, {call.from_user.full_name}!",
        reply_markup=kb)
    await state.finish()


@dp.callback_query_handler(text='clear', state='*')
async def clear(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('История общения стёрта')
    await state.update_data(history=[{"question": None, "answer": None}])


def register_handlers_AI(dp: Dispatcher):
    dp.register_message_handler(chat_start, text=['start'])
    dp.register_message_handler(chat_talk, state=AI.talk)
    dp.register_message_handler(back, text=['back'])
    dp.register_message_handler(clear, text=['clear'])
