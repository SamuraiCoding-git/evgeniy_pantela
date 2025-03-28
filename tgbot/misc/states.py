from aiogram.fsm.state import StatesGroup, State


class PaymentStates(StatesGroup):
    email = State()

class DeeplinkStates(StatesGroup):
    source = State()
    target = State()
    link = State()
