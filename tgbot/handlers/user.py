from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.utils.markdown import hlink, hbold, hitalic, hblockquote

from tgbot.config import Config
from tgbot.keyboards.callback_data import AcceptCreditData
from tgbot.keyboards.inline import start_keyboard, buy_keyboard, offer_keyboard, product_keyboard, enter_keyboard, \
    payment_method_keyboard, credit_keyboard, approve_credit
from tgbot.misc.states import PaymentStates, CreditStates
from tgbot.utils.db_utils import get_repo
from tgbot.utils.payment_utils import Payment

user_router = Router()

@user_router.message(CommandStart(deep_link=True))
async def user_deeplink(message: Message, command: CommandObject, state: FSMContext, config: Config):
    print(command.args)
    await state.update_data(deeplink=command.args)
    repo = await get_repo(config)
    user = await repo.users.get_user_by_id(message.from_user.id)
    if not user:
        text = (
            f"При использовании бота вы соглашаетесь с "
            f"{hlink('офертой', 'https://e1daea51-9c17-4933-adcb-86779a620982.selstorage.ru/250216%20%D0%94%D0%BE%D0%B3%D0%BE%D0%B2%D0%BE%D1%80-%D0%BE%D1%84%D0%B5%D1%80%D1%82%D0%B0.docx')} "
            f"и {hlink('политикой конфиденциальности', 'https://e1daea51-9c17-4933-adcb-86779a620982.selstorage.ru/%D0%9F%D0%BE%D0%BB%D0%B8%D1%82%D0%B8%D0%BA%D0%B0_%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B4%D0%B5%D0%BD%D1%86%D0%B8%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D0%B8_%D0%98%D0%9F_%D0%9F%D0%B0%D0%BD%D1%82%D0%B5%D0%BB%D0%B0.docx')}."
        )
        await message.answer(text, reply_markup=offer_keyboard())
    else:
        deeplink = await repo.deeplink.get_deeplink_by_id(int(command.args))
        text = (hbold('Доступ к каналу "Первый шаг"\n'),
                'Видео уроки по базе языка Го, регулярные эфиры, ответы на вопросы\n',
                hitalic('Цена - 2.490 рублей | 325 рублей в месяц\n'),
                hbold('Доступ выдается навсегда'))
        photo = "AgACAgIAAxkBAAICr2fm3EJnFAGYDCkU45oAAQKV_fbXeQAC0-wxGx5fOEvs-Ge3FpT9jgEAAwIAA3kAAzYE"
        if deeplink.source == "video":
            video = deeplink.target
            await message.answer_video(
                video=video,
                caption=deeplink.link
            )
        else:
            await message.answer_photo(
                photo=photo,
                caption="\n".join(text),
                reply_markup=start_keyboard()
            )


@user_router.message(CommandStart())
async def user_start(message: Message, config: Config):
    repo = await get_repo(config)
    user = await repo.users.get_user_by_id(message.from_user.id)
    if user:
        text = (hbold('Доступ к каналу "Первый шаг"\n'),
                'Видео уроки по базе языка Го, регулярные эфиры, ответы на вопросы\n',
                hitalic('Цена - 2.490 рублей | 325 рублей в месяц\n'),
                hbold('Доступ выдается навсегда'))
        photo = "AgACAgIAAxkBAAICr2fm3EJnFAGYDCkU45oAAQKV_fbXeQAC0-wxGx5fOEvs-Ge3FpT9jgEAAwIAA3kAAzYE"
        await message.answer_photo(
            photo=photo,
            caption="\n".join(text),
            reply_markup=start_keyboard())
        return
    text = (
        f"При использовании бота вы соглашаетесь с "
        f"{hlink('офертой', 'https://e1daea51-9c17-4933-adcb-86779a620982.selstorage.ru/250405_%D0%9E%D1%84%D0%B5%D1%80%D1%82%D0%B0_%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF_%D0%BA_%D0%A2%D0%93_%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB%D1%83_%D0%B8%D1%81%D0%BF%D1%80.docx')} "
        f"и {hlink('политикой конфиденциальности', 'https://e1daea51-9c17-4933-adcb-86779a620982.selstorage.ru/%D0%9F%D0%BE%D0%BB%D0%B8%D1%82%D0%B8%D0%BA%D0%B0_%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B4%D0%B5%D0%BD%D1%86%D0%B8%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D0%B8_%D0%98%D0%9F_%D0%9F%D0%B0%D0%BD%D1%82%D0%B5%D0%BB%D0%B0.docx')}."
    )
    await message.answer(text, reply_markup=offer_keyboard())


@user_router.callback_query(F.data == "accept_offer")
async def accept_offer(call: CallbackQuery, config: Config, state: FSMContext):
    repo = await get_repo(config)
    data = await state.get_data()
    await call.message.delete()
    await repo.users.get_or_create_user(
        call.message.chat.id,
        call.message.chat.full_name,
        call.message.from_user.is_premium,
        call.message.chat.username,
        None if not data.get("deeplink") else int(data.get("deeplink")),
    )
    deeplink_target = ""
    if data.get("deeplink"):
        deeplink = await repo.deeplink.get_deeplink_by_id(int(data.get("deeplink")))
        text = (hbold('Доступ к каналу "Первый шаг"\n'),
                'Видео уроки по базе языка Го, регулярные эфиры, ответы на вопросы\n',
                hitalic('Цена - 2.490 рублей | 325 рублей в месяц\n'),
                hbold('Доступ выдается навсегда'))
        photo = "AgACAgIAAxkBAAICr2fm3EJnFAGYDCkU45oAAQKV_fbXeQAC0-wxGx5fOEvs-Ge3FpT9jgEAAwIAA3kAAzYE"
        if deeplink.source == "video":
            video = deeplink.target
            await call.message.answer_video(
                video=video,
                caption=deeplink.link
            )
        else:
            await call.message.answer_photo(
                photo=photo,
                caption="\n".join(text),
                reply_markup=start_keyboard()
            )
    else:
        await state.clear()
        text = (hbold('Доступ к каналу "Первый шаг"\n'),
                'Видео уроки по базе языка Го, регулярные эфиры, ответы на вопросы\n',
                hitalic('Цена - 2.490 рублей | 325 рублей в месяц\n'),
                hbold('Доступ выдается навсегда'))
        photo = "AgACAgIAAxkBAAICr2fm3EJnFAGYDCkU45oAAQKV_fbXeQAC0-wxGx5fOEvs-Ge3FpT9jgEAAwIAA3kAAzYE"
        await call.message.answer_photo(
            photo=photo,
            caption="\n".join(text),
            reply_markup=start_keyboard())


@user_router.callback_query(F.data == "credit")
async def credit(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Оплатить:", reply_markup=credit_keyboard())

@user_router.callback_query(F.data == "paid_credit")
async def paid_credit(call: CallbackQuery, config: Config, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Отправьте скриншот:")
    await state.set_state(CreditStates.screenshot)

@user_router.message(CreditStates.screenshot)
async def screenshot(message: Message, config: Config, bot: Bot, state: FSMContext):
    if not message.photo:
        await message.answer("Отправь фото:")
        return
    for admin in config.tg_bot.admin_ids:
        await bot.send_photo(
            chat_id=admin,
            photo=message.photo[-1].file_id,
            reply_markup=approve_credit(message.from_user.id)
        )
    await message.answer("Скриншот направлен администратору!")
    await state.clear()

@user_router.callback_query(AcceptCreditData.filter())
async def accept_credit(call: CallbackQuery, config: Config, state: FSMContext, callback_data: AcceptCreditData, bot: Bot):
    response = callback_data.response
    await call.message.answer("Ответ направлен пользователю")
    if response:
        repo = await get_repo(config)
        link = await bot.create_chat_invite_link(
            config.tg_bot.channel_id,
            name=str(call.message.chat.id),
            member_limit=1
        )
        await bot.send_message(
            chat_id=callback_data.chat_id,
            text="Ссылка на канал: ",
                    reply_markup=enter_keyboard(link.invite_link))
        product = await repo.products.get_product_by_id(product_id=1)
        purchase = await repo.purchases.create_purchase(
            callback_data.chat_id,
            1,
            int(product.price)
        )
        await repo.purchases.toggle_is_paid(purchase.id)
    else:
        await bot.send_message(
            chat_id=callback_data.chat_id,
            text="Не оплачено")


@user_router.callback_query(F.data == "onetime")
async def onetime(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Введите email для получения чека:")
    await state.set_state(PaymentStates.email)

@user_router.callback_query(F.data == "buy")
async def buy_callback(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    text = ("Выберите способ оплаты:\n",
            "Доступ выдается навсегда")
    await call.message.answer("\n".join(text), reply_markup=payment_method_keyboard())
    await state.set_state(PaymentStates.email)


@user_router.message(PaymentStates.email)
async def payment_email(message: Message, state: FSMContext, config: Config):
    repo = await get_repo(config)
    tripwire = await repo.products.get_product_by_id(product_id=1)
    description = str(tripwire.description).replace('+br+', '\n')
    text = f"{tripwire.name}\n\n{description}"
    purchase = await repo.purchases.get_purchase_by_user(message.from_user.id)
    if not purchase:
        product = await repo.products.get_product_by_id(product_id=1)
        purchase = await repo.purchases.create_purchase(
            message.from_user.id,
            1,
            int(product.price)
        )
        payment = Payment(
            config.payment.terminal_key,
            config.payment.password
        )
        await payment.create_payment(
            str(purchase.id),
            product.name,
            message.text,
            product,
            repo
        )
        payment_url = payment.get_url
    else:
        payment_url = purchase.link
    await message.answer(text, reply_markup=product_keyboard(payment_url))

@user_router.callback_query(F.data == "check_payment")
async def check_payment_callback(call: CallbackQuery, bot: Bot, config: Config):
    repo = await get_repo(config)
    purchase = await repo.purchases.get_purchase_by_user(call.message.chat.id)
    if purchase.is_paid:
        await call.answer("Оплата прошла", show_alert=True)
        return
    payment = Payment(
        config.payment.terminal_key,
        config.payment.password
    )
    status = payment.get_payment_status(str(purchase.payment_id))
    if status:
        await call.answer("Оплата прошла", show_alert=True)
        text = ("Оплата",
                f"{call.message.chat.id} {'@' + call.message.chat.username if call.message.chat.username else ''}",
                f"{purchase.amount}₽"
                )
        for admin in config.tg_bot.admin_ids:
            await bot.send_message(
                chat_id=admin,
                text="\n".join(text)
            )
        await repo.purchases.toggle_is_paid(purchase.id)
        link = await bot.create_chat_invite_link(
            config.tg_bot.channel_id,
            name=str(call.message.chat.id),
            member_limit=1
        )
        await call.message.answer("Ссылка на канал: ",
                                  reply_markup=enter_keyboard(link.invite_link))

    else:
        await call.answer("Оплата не прошла", show_alert=True)


@user_router.callback_query(F.data == "about")
async def about_callback(call: CallbackQuery, config: Config):
    photo = "AgACAgIAAxkBAAICr2fm3EJnFAGYDCkU45oAAQKV_fbXeQAC0-wxGx5fOEvs-Ge3FpT9jgEAAwIAA3kAAzYE"
    text = (
        hbold('Что внутри?\n'),
        hblockquote('Видео уроки по следующим темам:'),
        '\n1. Основные ХТТП методы',
        '2. Что такое Рест Апи?',
        '3. Что такое Git',
        '4. Что такое реляционная База Данных',
        '5. Работа с БД\n',
        hblockquote('Вместе пишем проекты:\n'),
        '\n1. Создаем игру "камень, ножницы, бумага" с работающим сайтом',
        '2. Создаем генератор случайных цитат (CRUD операции)',
        '3. Делаем стену из ВКонтакте'
    )
    media = InputMediaPhoto(
        media=photo,
        caption="\n".join(text),
    )
    await call.message.edit_media(
        media=media,
        reply_markup=buy_keyboard())

@user_router.callback_query(F.data == "back")
async def back_callback(call: CallbackQuery, config: Config):
    photo = "AgACAgIAAxkBAAICr2fm3EJnFAGYDCkU45oAAQKV_fbXeQAC0-wxGx5fOEvs-Ge3FpT9jgEAAwIAA3kAAzYE"
    text = (hbold('Доступ к каналу "Первый шаг"\n'),
            'Видео уроки по базе языка Го, регулярные эфиры, ответы на вопросы\n',
            hitalic('Цена - 2.490 рублей | 325 рублей в месяц\n'),
            hbold('Доступ выдается навсегда'))
    media = InputMediaPhoto(
        media=photo,
        caption="\n".join(text)
    )
    await call.message.edit_media(
        media=media,
        reply_markup=start_keyboard())
