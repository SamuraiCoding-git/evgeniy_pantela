import logging

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, \
    InputMediaVideo, InputMediaAudio, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import SQLAlchemyError

from tgbot.config import _process_message
from tgbot.utils.db_utils import get_repo
from tgbot.utils.media import send_media, build_keyboard

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ScenarioHandler:
    def __init__(self, message: Message, state: FSMContext, config, params=None):
        self.message = message
        self.state = state
        self.config = config
        self.params = params or {}
        self.callbacks = {}

    async def handle_scenario(self, scenario: dict):
        self.callbacks = scenario.get("callbacks", {})
        await self.state.update_data(callbacks=self.callbacks)  # ← Сохраняем в FSM
        actions = scenario.get("actions", [])
        for action in actions:
            await self.handle_action(action)


    async def handle_action(self, action: dict):
        action_type = action.get("action")
        params = action.get("params", {})

        if action_type == "execute_function":
            await self.handle_execute_function(params)
        elif action_type == "send_text":
            await self.handle_send_text(params)
        elif action_type.startswith("send_"):
            await self.handle_send_media(action_type, params)
        else:
            logger.warning(f"Unknown action type: {action_type}")

    async def handle_execute_function(self, params: dict):
        functions = params.get("functions", [])
        for func in functions:
            await self.execute_function(func.get("function_name"), func.get("params", {}))

    async def handle_send_text(self, params: dict):
        try:
            text = params.get("text", "Default Text Message")
            keyboard_data = params.get("keyboard", [])
            keyboard = await build_keyboard(keyboard_data)

            sent_message = await self.message.answer(
                text=_process_message(text),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

            if "update_keyboard" in params:
                await self.update_keyboard(params["update_keyboard"], sent_message)

        except TelegramBadRequest as e:
            logger.exception(f"Failed to send text message: {e}")

    async def handle_send_media(self, media_type: str, params: dict):
        try:
            sent_message = await send_media(self.message, media_type, params)
            if "update_keyboard" in params:
                await self.update_keyboard(params["update_keyboard"], sent_message)
        except Exception as e:
            logger.exception(f"Failed to send media {media_type}: {e}")

    async def execute_function(self, function_path: str, params: dict):
        if not function_path:
            return

        try:
            if function_path.startswith("send_"):
                await self.handle_send_media(function_path, params)
                return

            repo_name, func_name = function_path.split(".", 1)
            repo = await get_repo(self.config)
            repo_obj = getattr(repo, repo_name, None)
            if not repo_obj:
                raise AttributeError(f"Repository '{repo_name}' not found")

            func = getattr(repo_obj, func_name, None)
            if not func:
                raise AttributeError(f"Function '{func_name}' not found in '{repo_name}'")

            if "user_id" not in params:
                params["user_id"] = self.message.chat.id

            await func(**params)
            logger.info(f"Executed function: {function_path} with {params}")

        except (ValueError, AttributeError, SQLAlchemyError) as e:
            logger.exception(f"Error executing function {function_path}: {e}")
            await self.message.answer(f"Error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            await self.message.answer("An unexpected error occurred.")

    async def update_keyboard(self, update_params, sent_message):
        if isinstance(update_params, dict):
            new_keyboard_data = update_params.get("keyboard", [])
        else:
            new_keyboard_data = update_params

        if not new_keyboard_data:
            try:
                await sent_message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest as e:
                logger.exception(f"Error while removing keyboard: {e}")
            return

        new_keyboard = await build_keyboard(new_keyboard_data)

        try:
            if sent_message.content_type == 'text':
                await sent_message.edit_text(
                    text=sent_message.text,
                    reply_markup=new_keyboard
                )
            elif sent_message.content_type == 'photo':
                await sent_message.edit_media(
                    media=InputMediaPhoto(
                        media=sent_message.photo[0].file_id,
                        caption=sent_message.caption
                    ),
                    reply_markup=new_keyboard
                )
            elif sent_message.content_type == 'video':
                await sent_message.edit_media(
                    media=InputMediaVideo(
                        media=sent_message.video.file_id,
                        caption=sent_message.caption
                    ),
                    reply_markup=new_keyboard
                )
            elif sent_message.content_type == 'audio':
                await sent_message.edit_media(
                    media=InputMediaAudio(
                        media=sent_message.audio.file_id,
                        caption=sent_message.caption
                    ),
                    reply_markup=new_keyboard
                )
            else:
                logger.exception(f"Unsupported media type: {sent_message.content_type}")

        except TelegramBadRequest as e:
            logger.exception(f"Error while editing message: {e}. Sending a new message instead.")
            await self.message.answer(
                "Here is the updated content with new buttons.",
                reply_markup=new_keyboard
            )

    async def handle_callback(self, callback_id: str):
        """
        Обрабатывает callback_id по нажатию на кнопку.
        """
        data = await self.state.get_data()
        self.callbacks = data.get("callbacks", {})  # ← Загружаем сохранённые callbacks

        callback_actions = self.callbacks.get(callback_id)
        if not callback_actions:
            logger.warning(f"No callback actions for id {callback_id}")
            await self.message.answer("Произошла ошибка: действие не найдено.")
            return

        for action in callback_actions:
            function_name = action.get("function_name")
            params = action.get("params", {})

            if function_name == "send_text":
                await self.handle_send_text(params)
            elif function_name.startswith("send_"):
                await self.handle_send_media(function_name, params)
            else:
                await self.execute_function(function_name, params)
