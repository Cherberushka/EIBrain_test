from aiogram.dispatcher.filters.state import StatesGroup, State


class AI(StatesGroup):
    talk = State()
    wait = State()
    change_voice = State()
    type_answer = State()
