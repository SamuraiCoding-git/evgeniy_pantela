from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from tgbot.keyboards.callback_data import SourceData, TargetData, AcceptCreditData


def offer_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ПОДТВЕРДИТЬ", callback_data="accept_offer")
        ]
    ])
    return keyboard

def start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Купить", callback_data="buy")
        ],
        [
            InlineKeyboardButton(text="Подробнее", callback_data="about")
        ],
        [
            InlineKeyboardButton(text="Поддержка", url="https://t.me/pantelam")
        ],
    ])
    return keyboard

def buy_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Купить", callback_data="buy")
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back")
        ]
    ])
    return keyboard

def admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
          InlineKeyboardButton(text="Диплинк", callback_data="admin_deeplink")
        ],
        [
            InlineKeyboardButton(text="Статистика", callback_data="stats")
        ]
    ])
    return keyboard

def product_keyboard(url):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Оплатить", web_app=WebAppInfo(url=url))
        ],
        [
            InlineKeyboardButton(text="Оплатил", callback_data="check_payment")
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="back")
        ]
    ])
    return keyboard

def enter_keyboard(link):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Вступить", url=link)
        ]
    ])
    return keyboard

def deeplink_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Создать диплинк", callback_data="create_deeplink")
        ],
        # [
        #     InlineKeyboardButton(text="Список диплинков", callback_data="list_deeplink")
        # ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="admin_back")
        ]
    ])
    return keyboard

def source_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Telegram", callback_data=SourceData(source="telegram").pack()),
            InlineKeyboardButton(text="Youtube", callback_data=SourceData(source="youtube").pack()),
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="admin_back")
        ]
    ])
    return keyboard

def payment_method_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="325₽ в месяц", callback_data="credit")
        ],
        [
            InlineKeyboardButton(text="2490₽ ЕДИНОРАЗОВО", callback_data="onetime")
        ]
    ])
    return keyboard

def target_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Трипвайр", callback_data=TargetData(target="tripwire").pack()),
            InlineKeyboardButton(text="Главная", callback_data=TargetData(target="main").pack()),
        ],
        [
            InlineKeyboardButton(text="⏪ Назад", callback_data="admin_back")
        ]
    ])
    return keyboard

def credit_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="325₽ в месяц", url="https://link.tinkoff.ru/1tCdbBlTfq0")
        ],
        [
            InlineKeyboardButton(text="Оплатил", callback_data="paid_credit")
        ]
    ])
    return keyboard

def approve_credit(chat_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅", callback_data=AcceptCreditData(
                response=True,
                chat_id=chat_id
            ).pack()),
            InlineKeyboardButton(text="❌", callback_data=AcceptCreditData(
                response=False,
                chat_id=chat_id
            ).pack())
        ]
    ])
    return keyboard
