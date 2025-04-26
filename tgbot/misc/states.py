from aiogram.fsm.state import StatesGroup, State


class PaymentStates(StatesGroup):
    email = State()

class DeeplinkStates(StatesGroup):
    source = State()
    target = State()
    link = State()

class CreditStates(StatesGroup):
    screenshot = State()

class MailingStates(StatesGroup):
    message = State()
    buttons = State()
    private_user_id = State()

class GrantAccessStates(StatesGroup):
    chat_id = State()
