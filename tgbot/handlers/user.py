import json

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from tgbot.config import Config
from tgbot.keyboards.callback_data import AcceptCreditData
from tgbot.keyboards.inline import start_keyboard, buy_keyboard, offer_keyboard, product_keyboard, enter_keyboard, \
    payment_method_keyboard, credit_keyboard, approve_credit
from tgbot.misc.states import PaymentStates, CreditStates
from tgbot.utils.db_utils import get_repo
from tgbot.utils.deeplink_utils import ScenarioHandler
from tgbot.utils.payment_utils import Payment

user_router = Router()

# @user_router.message(Command("test_deeplink_132123"))
# async def start_handler(message: Message, state: FSMContext, config: Config):
#     scenario_json = """
# #     {
# #   "actions": [
# #     {
# #       "action": "send_text",
# #       "params": {
# #         "text": "Welcome! Here's some media content for you to explore.",
# #         "delay": 1
# #       }
# #     },
# #     {
# #   "action": "send_video",
# #   "params": {
# #     "video": {
# #       "url": "https://media-hosting.imagekit.io/bb639c2ad9ae4ef6/@dvachannel%20(1).mp4?Expires=1840146802&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=i8kkEZgWkzDfeZpYa1vPonksnGxUOeywVTNdRoGwGHgVYVxoDUR~ijHU71rvzI4M~XcFvVCWO0Mo183TbLOI9ayy2ybirQ5iEI5HfT~3cm3v4nncrdEpnJ08jfagqTu5B~LP0vB3icFZ3Gt7cPN38bS3ivwoER37HhilLu674Ia9U52Jhaw7D5tTnCfkg97yW1gz1sFK8zplYiG3TZ1h-dwLkt3FWKuOGdZiMuYGancDaU3Z-3Jid9w9ReDg2kAWq8GIQ9r~YOjx5Sgt76Xt0K~FoHrYQxTiZ2treoRk8PLRlrpHQObFEiXITkPHBPMEtwjfR8wNY0z0x70jysNV-Q__"
# #     },
# #     "caption": "Check out this video!",
#     "keyboard": [
#       [
#         {
#           "type": "url",
#           "text": "Go to Website",
#           "url": "https://www.google.com"
#         },
#         {
#           "type": "callback_data",
#           "text": "Buy Product",
#           "callback_data": "buy_product"
#         }
#       ],
#       [
#         {
#           "type": "web_app",
#           "text": "Open Web App",
#           "web_app": "https://www.google.com"
#         }
#       ]
#     ],
# #     "delay": 1,
# #     "update_keyboard": {
# #       "keyboard": [
# #
# #       ],
# #       "delay": 2
# #         }
# #       }
# #     },
# #     {
# #       "action": "send_photo",
# #       "params": {
# #         "photo": {
# #           "url": "https://is1-ssl.mzstatic.com/image/thumb/Music122/v4/e1/57/3e/e1573e85-943a-1370-db52-c1ed0d3d4b49/859784551631_cover.jpg/1200x1200bb.jpg"
# #         },
# #         "caption": "Here is a photo!",
# #         "keyboard": [
# #           [
# #             {
# #               "type": "callback_data",
# #               "text": "Product Details",
# #               "callback_data": "product_details"
# #             },
# #             {
# #               "type": "url",
# #               "text": "Visit Google",
# #               "url": "https://www.google.com"
# #             }
# #           ],
# #           [
# #             {
# #               "type": "execute_function",
# #               "text": "Update User",
# #               "function_name": "users.update_user",
# #               "args": {
# #                 "username": "new_username"
# #               }
# #             }
# #           ]
# #         ],
# #         "delay": 1
# #       }
# #     },
# #     {
# #       "action": "send_document",
# #       "params": {
# #         "document": {
# #           "id": "BQACAgIAAxkBAAIH0WgK16rSiR3i4Gdze5oeeiq31dfZAALaeQACn2NZSM8ZIPu8YzCRNgQ"
# #         },
# #         "caption": "Here is a document!",
# #         "keyboard": [
# #           [
# #             {
# #               "type": "web_app",
# #               "text": "Open App",
# #               "web_app": "https://www.google.com"
# #             },
# #             {
# #               "type": "callback_data",
# #               "text": "Support",
# #               "callback_data": "support"
# #             }
# #           ]
# #         ],
# #         "delay": 1
# #       }
# #     }
# #   ]
# # }
#     """
#
#     scenario_handler = ScenarioHandler(message, state, config)
#     await scenario_handler.handle_scenario(scenario_json)

@user_router.callback_query(F.data.startswith('execute_function:'))
async def handle_execute_function(callback_query: CallbackQuery, state: FSMContext, config: Config):
    data = await state.get_data()

    callback_data = callback_query.data.split(":", 2)  # Ограничиваем на 3 части: 'params', 'function_name', 'params_data'

    print(len(callback_data))

    if len(callback_data) != 2:
        await callback_query.answer("Invalid callback data format.")
        return

    # Извлекаем название функции и сериализованные параметры
    unique_id = callback_data[0]  # Имя функции

    params = data.get(unique_id)

    print(params)

    # try:
    #     # Десериализуем параметры
    #     params = json.loads(serialized_params)
    # except json.JSONDecodeError:
    #     await callback_query.answer("Error decoding parameters.")
    #     return
    #
    # # Добавляем user_id в параметры
    # params["user_id"] = callback_query.from_user.id
    #
    # # Создаем экземпляр ScenarioHandler
    # scenario_handler = ScenarioHandler(callback_query.message, state, config)
    #
    # # Вызываем метод execute_function внутри класса с переданными параметрами
    # await scenario_handler.execute_function(function_name, params)

    # Ответ пользователю
    # await callback_query.answer(f"Executing function {function_name} with parameters.")

@user_router.message(CommandStart(deep_link=True))
async def user_deeplink(message: Message, command: CommandObject, state: FSMContext, config: Config):
    await state.update_data(deeplink=command.args)
    repo = await get_repo(config)
    user = await repo.users.get_user_by_id(message.from_user.id)
    if not user:
        text = config.messages.offer_agreement
        await message.answer(text, reply_markup=offer_keyboard())
    else:
        deeplink = await repo.deeplink.get_deeplink_by_id(int(command.args))
        scenario_handler = ScenarioHandler(message, state, config)
        await scenario_handler.handle_scenario(json.loads(deeplink.scenario))


@user_router.message(CommandStart())
async def user_start(message: Message, config: Config):
    repo = await get_repo(config)
    user = await repo.users.get_user_by_id(message.from_user.id)
    if user:
        text = config.messages.course_intro
        photo = config.messages.photo_go_intro
        await message.answer_photo(
            photo=photo,
            caption="\n".join(text),
            reply_markup=start_keyboard())
        return
    text = config.messages.offer_agreement
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
    if data.get("deeplink"):
        deeplink = await repo.deeplink.get_deeplink_by_id(int(data.get("deeplink")))
        scenario_handler = ScenarioHandler(call.message, state, config)
        await scenario_handler.handle_scenario(json.loads(deeplink.scenario))
    else:
        await state.clear()
        text = config.messages.course_intro
        photo = config.messages.photo_go_intro
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
    photo = config.messages.photo_go_intro
    text = config.messages.about_course

    media = InputMediaPhoto(
        media=photo,
        caption="\n".join(text),
    )
    await call.message.edit_media(
        media=media,
        reply_markup=buy_keyboard())

@user_router.callback_query(F.data == "back")
async def back_callback(call: CallbackQuery, config: Config):
    photo = config.messages.photo_go_intro
    text = config.messages.course_intro
    media = InputMediaPhoto(
        media=photo,
        caption="\n".join(text)
    )
    await call.message.edit_media(
        media=media,
        reply_markup=start_keyboard())
