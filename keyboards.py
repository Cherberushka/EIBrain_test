from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

on_speech_answer = InlineKeyboardButton('Включить озвучивание ответа', callback_data='on_sa')
off_speech_answer = InlineKeyboardButton('Выключить озвучивание ответа', callback_data='off_sa')

keyboard_speech_answer = InlineKeyboardMarkup(row_width=1).add(on_speech_answer, off_speech_answer)

