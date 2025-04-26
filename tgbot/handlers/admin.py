import asyncio
import os
from datetime import datetime
from linecache import cache

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from aiogram.utils.deep_linking import create_start_link

from tgbot.config import Config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.callback_data import SourceData, TargetData, AudienceData
from tgbot.keyboards.inline import admin_keyboard, deeplink_keyboard, source_keyboard, target_keyboard, \
    statistics_keyboard, mailing_keyboard, create_url_keyboard, audience_keyboard, confirm_mailing_keyboard, \
    enter_keyboard, admin_back_keyboard
from tgbot.misc.states import DeeplinkStates, MailingStates, GrantAccessStates
from tgbot.utils.admin_utils import save_to_excel, process_mailing_data
from tgbot.utils.db_utils import get_repo

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("admin"))
async def admin_start(message: Message):
    await message.answer("Привет, админ!", reply_markup=admin_keyboard())


@admin_router.callback_query(F.data == "admin_deeplink")
async def admin_deeplink(call: CallbackQuery):
    await call.message.edit_text("Меню диплинков: ", reply_markup=deeplink_keyboard())

@admin_router.callback_query(F.data == "create_deeplink")
async def admin_deeplink(call: CallbackQuery, config: Config):
    await call.message.edit_text("Выбери источник: ", reply_markup=source_keyboard())


@admin_router.callback_query(SourceData.filter())
async def source_admin(call: CallbackQuery, callback_data: SourceData, state: FSMContext):
    await state.update_data(source=callback_data.source)
    await call.message.edit_text("Выбери цель: ", reply_markup=target_keyboard())

@admin_router.callback_query(TargetData.filter())
async def target_admin(call: CallbackQuery, callback_data: TargetData, state: FSMContext):
    await state.update_data(target=callback_data.target)
    await state.set_state(DeeplinkStates.link)
    await call.message.edit_text("Введи ссылку: ")

@admin_router.message(DeeplinkStates.link)
async def deeplink_link(message: Message, config: Config, state: FSMContext, bot: Bot):
    repo = await get_repo(config)
    data = await state.get_data()
    deeplink = await repo.deeplink.create_deeplink(
        data.get("source"),
        data.get("target"),
        message.text
    )
    link = await create_start_link(bot, str(deeplink.id))
    await message.answer(f"Диплинк: {link}")

@admin_router.callback_query(F.data == "stats")
async def admin_stats(call: CallbackQuery, config: Config):
    repo = await get_repo(config)
    users_count = await repo.purchases.count_users()
    paid_users_count = await repo.purchases.get_paid_users_count()
    text = (
        f"Количество пользователей: {users_count}\n",
        f"Количество покупок: {paid_users_count}"
    )
    await call.message.answer("\n".join(text), reply_markup=statistics_keyboard())


@admin_router.callback_query(F.data == "table")
async def admin_table(call: CallbackQuery, config: Config):
    repo = await get_repo(config)
    users = await repo.users.get_all_users()

    if not users:
        await call.message.answer("Пользователи не найдены.")
        return

    save_to_excel(users)

    # file = FSInputFile(path="/Users/matvejdoroshenko/PycharmProjects/evgeniy_pantela/output.xlsx")
    file = FSInputFile(path="/root/evgeniy_pantela/output.xlsx")
    await call.message.answer_document(document=file)
    os.remove("/root/evgeniy_pantela/output.xlsx")


@admin_router.callback_query(F.data == "mailing")
async def admin_mailing(call: CallbackQuery, config: Config, state: FSMContext):
    await call.message.edit_text("Отправь сообщение: ", reply_markup=admin_back_keyboard())
    await state.set_state(MailingStates.message)


@admin_router.message(MailingStates.message)
async def mailing_message(message: Message, state: FSMContext):
    await message.delete()
    success = await process_mailing_data(message, state)
    if not success:
        await message.answer("Тип сообщения не поддерживается. Отправь текст, медиа или документ.",
                             reply_markup=admin_back_keyboard())
        return

    await message.answer("Настройка рассылки:", reply_markup=mailing_keyboard())


@admin_router.callback_query(F.data == "preview")
async def preview_mailing(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    content_type = data.get("content_type")
    content = data.get("content")
    file_id = data.get("file_id")
    buttons = data.get("buttons", [])

    if not content_type:
        await call.answer("Нет данных для предпросмотра. Сначала добавь сообщение.", show_alert=True)
        return

    reply_markup = create_url_keyboard(buttons, preview=True)

    send_kwargs = {
        "caption": content,
        "reply_markup": reply_markup
    } if content_type != "text" else {
        "text": content,
        "reply_markup": reply_markup
    }

    match content_type:
        case "text":
            await call.message.answer(**send_kwargs)
        case "photo":
            await call.message.answer_photo(photo=file_id, **send_kwargs)
        case "video":
            await call.message.answer_video(video=file_id, **send_kwargs)
        case "animation":
            await call.message.answer_animation(animation=file_id, **send_kwargs)
        case "audio":
            await call.message.answer_audio(audio=file_id, **send_kwargs)
        case "document":
            await call.message.answer_document(document=file_id, **send_kwargs)
        case "sticker":
            await call.message.answer_sticker(sticker=file_id, **send_kwargs)
        case "video_note":
            await call.message.answer_video_note(video_note=file_id, **send_kwargs)
        case "voice":
            await call.message.answer_voice(voice=file_id, **send_kwargs)
        case _:
            await call.message.answer("Не удалось отобразить данный тип контента.")

@admin_router.callback_query(F.data == "mailing_buttons")
async def ask_for_buttons(call: CallbackQuery, state: FSMContext):
    await state.set_state(MailingStates.buttons)
    await call.message.edit_text(
        "Отправь кнопки в формате:\n\n"
        "Название кнопки 1 - https://example.com\n"
        "Название кнопки 2 - https://example.org\n\n"
        "Каждая кнопка — на новой строке.",
        reply_markup=admin_back_keyboard()
    )


@admin_router.message(MailingStates.buttons)
async def mailing_buttons(message: Message, state: FSMContext):
    await message.delete()
    lines = message.text.strip().splitlines()
    buttons = []

    for line in lines:
        if " - " in line:
            text, url = line.split(" - ", 1)
            buttons.append({"text": text.strip(), "url": url.strip()})
        else:
            await message.answer(f"Неверный формат строки: {line}")
            return

    await state.update_data(buttons=buttons)
    await message.answer("Кнопки успешно добавлены!\nНастройка рассылки:",
                         reply_markup=mailing_keyboard())

@admin_router.callback_query(F.data == "admin_mailing")
async def admin_mailing(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Настройка рассылки:",
                                 reply_markup=mailing_keyboard())

@admin_router.callback_query(F.data == "send")
async def send_mailing(call: CallbackQuery):
    await call.message.edit_text(
        "Выберите аудиторию: ",
        reply_markup=audience_keyboard()
    )

@admin_router.callback_query(AudienceData.filter())
async def audience_data(call: CallbackQuery, callback_data: AudienceData, state: FSMContext, config: Config):
    await state.update_data(target_audience=callback_data.audience)
    if callback_data.audience == "private":
        await state.set_state(MailingStates.private_user_id)
        await call.message.edit_text("Введи user_id пользователя: ")
        return
    await call.message.edit_text(
        "Подтвердить рассылку:",
        reply_markup=confirm_mailing_keyboard()
    )

@admin_router.message(MailingStates.private_user_id)
async def private_user_id(message: Message, state: FSMContext):
    await state.update_data(private_user_id=message.text)
    await message.answer(
        "Подтвердить рассылку:",
        reply_markup=confirm_mailing_keyboard()
    )


@admin_router.callback_query(F.data == "confirm_mailing")
async def confirm_mailing(call: CallbackQuery, config: Config, state: FSMContext):
    await call.message.delete()
    repo = await get_repo(config)
    data = await state.get_data()

    content_type = data.get("content_type")
    content = data.get("content")
    file_id = data.get("file_id")
    buttons = data.get("buttons", [])
    target_audience = data.get("target_audience")


    # Получение целевой аудитории
    if target_audience == "all":
        users = await repo.users.get_all_users()
    elif target_audience == "bought":
        users = await repo.users.get_users_with_payment()
    elif target_audience == "nonbought":
        users = await repo.users.get_users_without_payment()
    elif target_audience == "private":
        private_user_id = data.get("private_user_id")
        users = [
            {"user":
                 {"id": int(private_user_id)}
            }
        ]
    else:
        await call.answer("Не удалось определить аудиторию.", show_alert=True)
        return

    user_ids = [user["user"].id for user in users]
    reply_markup = create_url_keyboard(buttons) if buttons else None

    send_kwargs = {
        "caption": content,
        "reply_markup": reply_markup
    } if content_type != "text" else {
        "text": content,
        "reply_markup": reply_markup
    }

    error_logs = []
    success, failed = 0, 0

    for user_id in user_ids:
        try:
            match content_type:
                case "text":
                    await call.bot.send_message(chat_id=user_id, **send_kwargs)
                case "photo":
                    await call.bot.send_photo(chat_id=user_id, photo=file_id, **send_kwargs)
                case "video":
                    await call.bot.send_video(chat_id=user_id, video=file_id, **send_kwargs)
                case "animation":
                    await call.bot.send_animation(chat_id=user_id, animation=file_id, **send_kwargs)
                case "audio":
                    await call.bot.send_audio(chat_id=user_id, audio=file_id, **send_kwargs)
                case "document":
                    await call.bot.send_document(chat_id=user_id, document=file_id, **send_kwargs)
                case "sticker":
                    await call.bot.send_sticker(chat_id=user_id, sticker=file_id, **send_kwargs)
                case "video_note":
                    await call.bot.send_video_note(chat_id=user_id, video_note=file_id, **send_kwargs)
                case "voice":
                    await call.bot.send_voice(chat_id=user_id, voice=file_id, **send_kwargs)
                case _:
                    failed += 1
                    error_logs.append(f"[{user_id}] ❌ Unsupported content type: {content_type}")
                    continue
            success += 1
            await asyncio.sleep(0.03)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramForbiddenError:
            failed += 1
            error_logs.append(f"[{user_id}] ❌ Bot was blocked by user.")
        except Exception as e:
            failed += 1
            error_logs.append(f"[{user_id}] ❌ {repr(e)}")

    await call.message.answer(f"Рассылка завершена ✅\nУспешно: {success}\nОшибок: {failed}")

    if error_logs:
        print(error_logs)
        log_filename = f"mailing_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(error_logs))

        await call.message.answer_document(FSInputFile(log_filename))


@admin_router.callback_query(F.data == "grant_access")
async def grant_access(call: CallbackQuery, config: Config, state: FSMContext):
    await call.message.edit_text(
        "Отправь user_id человека для выдачи доступа:",
        reply_markup=admin_back_keyboard()
    )
    await state.set_state(GrantAccessStates.chat_id)

@admin_router.message(GrantAccessStates.chat_id)
async def grant_access(message: Message, state: FSMContext, config: Config, bot: Bot):
    repo = await get_repo(config)
    user = await repo.users.get_user_by_id(int(message.text))
    if not user:
        await message.answer("Пользователя нет в базе!")
        return
    purchase = await repo.purchases.create_purchase(
        int(message.text),
        1,
        2490
    )
    await repo.purchases.toggle_is_paid(purchase.id)
    link = await bot.create_chat_invite_link(
        config.tg_bot.channel_id,
        name=message.text,
        member_limit=1
    )
    await bot.send_message(
        chat_id=int(message.text),
        text="Ссылка на канал: ",
        reply_markup=enter_keyboard(link.invite_link)
    )
    await message.answer("Доступ успешно выдан!")

@admin_router.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer("Привет, админ!", reply_markup=admin_keyboard())
