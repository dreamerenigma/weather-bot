from aiogram.fsm.state import StatesGroup, State


class BotForm(StatesGroup):
    waiting_for_city = State()
    waiting_for_new_city = State()


class Form(StatesGroup):
    city = State()
