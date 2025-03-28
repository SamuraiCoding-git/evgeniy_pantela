from linecache import cache

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import create_start_link

from tgbot.config import Config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.callback_data import SourceData, TargetData
from tgbot.keyboards.inline import admin_keyboard, deeplink_keyboard, source_keyboard, target_keyboard
from tgbot.misc.states import DeeplinkStates
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
    await call.message.answer("\n".join(text))


@admin_router.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Привет, админ!", reply_markup=admin_keyboard())
