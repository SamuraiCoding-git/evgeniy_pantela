import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import logging

from aiogram.types import WebAppInfo

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import logging
import json
import asyncio
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto, InputMediaVideo, \
    URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.utils.db_utils import get_repo

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ScenarioHandler:
    def __init__(self, message: Message, state: FSMContext, config):
        self.message = message
        self.state = state
        self.config = config

    async def handle_scenario(self, scenario: dict):
        """
        Основной метод для обработки сценария.
        Преобразует JSON в структуру данных и проигрывает сценарий.
        """
        scenario_data = scenario
        await self.play_scenario(scenario_data)

    async def play_scenario(self, scenario_data):
        """
        Проигрывает сценарий на основе данных из JSON
        """
        actions = scenario_data.get("actions", [])
        for action in actions:
            action_type = action.get("action")
            params = action.get("params", {})

            handler_class = self.get_handler(action_type)
            if handler_class:
                handler = handler_class(self.message, params, self.state, self.config)
                await handler.send()

                # После отправки сохраняем sent_message
                sent_message = handler.sent_message

                if action_type == "execute_function":
                    functions = params.get("functions", [])
                    for function in functions:
                        function_name = function.get("function_name")
                        function_params = function.get("params", {})
                        await self.execute_function(function_name, function_params)

                if "delay" in params:
                    await asyncio.sleep(params["delay"])

                if "update_keyboard" in params:
                    await self.update_keyboard(params["update_keyboard"], sent_message)
            else:
                logger.warning(f"Unknown action type: {action_type}")

    async def execute_function(self, function_path: str, params: dict):
        """
        Выполняет несколько функций, переданных в params.
        """
        try:
            functions = params.get("functions", [])

            # Обработка нескольких функций
            for function in functions:
                function_name = function.get("function_name")
                function_params = function.get("params", {})
                result = await self._execute_single_function(function_name, function_params)
                logger.info(f"Executed function '{function_name}' with params: {function_params}")

            return result

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await self.message.answer(f"Unexpected error: {e}")

    async def _execute_single_function(self, function_name: str, params: dict):
        """
        Выполняет одну функцию, используя её имя и параметры.
        """
        try:
            repo_name, func_name = function_name.split(".")
            repo = await get_repo(self.config)

            repo_func = getattr(repo, repo_name, None)
            if not repo_func:
                raise AttributeError(f"Repository '{repo_name}' does not exist.")

            function = getattr(repo_func, func_name, None)
            if not function:
                raise AttributeError(f"Function '{func_name}' does not exist.")

            if "user_id" not in params:
                params["user_id"] = self.message.chat.id

            result = await function(**params)
            return result
        except Exception as e:
            logger.error(f"Error in function '{function_name}': {e}")
            return None

    async def send_video(self, params):
        """
        Отправка видео.
        """
        video_id = params.get("video_id")
        if video_id:
            self.sent_message = await self.message.answer_video(video_id)
            await self.update_keyboard(params.get("keyboard", []), self.sent_message)

    @staticmethod
    def get_handler(action_type: str):
        """
        Возвращает соответствующий обработчик для типа действия.
        """
        media_handlers = {
            "send_video": VideoHandler,
            "send_audio": AudioHandler,
            "send_document": DocumentHandler,
            "send_photo": PhotoHandler,
            "send_sticker": StickerHandler,
            "send_video_note": VideoNoteHandler,
            "send_voice": VoiceHandler,
            "send_media_group": MediaGroupHandler,
        }

        button_handlers = {
            "url": ButtonHandler,
            "web_app": ButtonHandler,
            "callback_data": ButtonHandler,
            "execute_function": ButtonHandler,
        }

        # Проверка для медиа
        handler = media_handlers.get(action_type)
        if handler:
            return handler

        # Проверка для кнопок
        handler = button_handlers.get(action_type)
        if handler:
            return handler

        return None

    async def create_keyboard(self, params: dict):
        """
        Создание многоуровневой клавиатуры на основе данных из сценария.
        """
        keyboard_data = params.get("keyboard", [])
        keyboard = []

        for row in keyboard_data:
            button_row = []
            for button in row:
                button_type = button.get("type", "callback_data")

                # Для кнопок типа execute_function
                if button_type == "execute_function":
                    function_params = button.get("params", {})
                    serialized_params = json.dumps(function_params)

                    button_row.append(InlineKeyboardButton(
                        text=button["text"],
                        callback_data=f"params:{button.get('function_name')}:{serialized_params}"
                    ))

                # Обработка других типов кнопок
                elif button_type == "url":
                    button_row.append(InlineKeyboardButton(
                        text=button["text"],
                        url=button.get("url")
                    ))
                elif button_type == "web_app":
                    button_row.append(InlineKeyboardButton(
                        text=button["text"],
                        web_app=WebAppInfo(url=button.get("web_app"))
                    ))
                elif button_type == "callback_data":
                    button_row.append(InlineKeyboardButton(
                        text=button["text"],
                        callback_data=button.get("callback_data")
                    ))

            keyboard.append(button_row)

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def update_keyboard(self, update_params, sent_message):
        """
        Обновление клавиатуры через delay и новый набор кнопок.
        """
        if isinstance(update_params, dict):
            new_keyboard_data = update_params.get("keyboard", [])
        else:
            new_keyboard_data = update_params

        if not new_keyboard_data:
            try:
                await sent_message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest as e:
                logger.error(f"Error while removing keyboard: {e}")
            return

        new_keyboard = []
        for button_row in new_keyboard_data:
            button_row_markup = []
            for button in button_row:
                button_type = button.get("type", "callback_data")

                if button_type == "url":
                    button_row_markup.append(InlineKeyboardButton(
                        text=button["text"],
                        url=button.get("url")
                    ))
                elif button_type == "web_app":
                    button_row_markup.append(InlineKeyboardButton(
                        text=button["text"],
                        web_app=WebAppInfo(url=button.get("web_app"))
                    ))
                elif button_type == "callback_data":
                    button_row_markup.append(InlineKeyboardButton(
                        text=button["text"],
                        callback_data=button.get("callback_data")
                    ))
                elif button_type == "execute_function":
                    button_row_markup.append(InlineKeyboardButton(
                        text=button["text"],
                        callback_data=f"execute_function:{button.get('function_name')}"
                    ))

            new_keyboard.append(button_row_markup)

        try:
            await sent_message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard))
        except TelegramBadRequest as e:
            logger.error(f"Error while editing message: {e}. Sending a new message instead.")
            await self.message.answer(
                "Here is the updated content with new buttons.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
            )


class MediaHandler(ScenarioHandler):
    def __init__(self, message: Message, params: dict, state: FSMContext, config):
        super().__init__(message, state, config)
        self.message = message
        self.params = params
        self.sent_message = None  # Сохраняем объект отправленного сообщения

    async def send(self):
        raise NotImplementedError("Method 'send' should be implemented.")


class VideoHandler(MediaHandler):
    async def send(self):
        video_url = self.params.get("video", {}).get("url", "")
        video_id = self.params.get("video", {}).get("id", "")
        caption = self.params.get("caption", "")

        # Отправляем видео и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_video(
            URLInputFile(video_url) if video_url else video_id,
            caption=caption,
            reply_markup=await self.create_keyboard(self.params)
        )


class AudioHandler(MediaHandler):
    async def send(self):
        audio_url = self.params.get("audio", {}).get("url", "")
        audio_id = self.params.get("audio", {}).get("id", "")
        caption = self.params.get("caption", "")

        # Отправляем аудио и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_audio(
            URLInputFile(audio_url) if audio_url else audio_id,
            caption=caption,
            reply_markup=await self.create_keyboard(self.params)
        )


class DocumentHandler(MediaHandler):
    async def send(self):
        document_url = self.params.get("document", {}).get("url", "")
        document_id = self.params.get("document", {}).get("id", "")
        caption = self.params.get("caption", "")

        # Отправляем документ и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_document(
            URLInputFile(document_url) if document_url else document_id,
            caption=caption,
            reply_markup=await self.create_keyboard(self.params)
        )


class PhotoHandler(MediaHandler):
    async def send(self):
        photo_url = self.params.get("photo", {}).get("url", "")
        photo_id = self.params.get("photo", {}).get("id", "")
        caption = self.params.get("caption", "")

        # Отправляем фото и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_photo(
            URLInputFile(photo_url) if photo_url else photo_id,
            caption=caption,
            reply_markup=await self.create_keyboard(self.params)
        )


class StickerHandler(MediaHandler):
    async def send(self):
        sticker_id = self.params.get("id", "")
        caption = self.params.get("caption", "")

        # Отправляем стикер и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_sticker(
            sticker_id,
            caption=caption,
            reply_markup=await self.create_keyboard(self.params)
        )


class VideoNoteHandler(MediaHandler):
    async def send(self):
        video_note_id = self.params.get("id", "")
        caption = self.params.get("caption", "")

        # Отправляем видеозаметку и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_video_note(
            video_note_id,
            caption=caption,
            reply_markup=await self.create_keyboard(self.params)
        )


class VoiceHandler(MediaHandler):
    async def send(self):
        voice_id = self.params.get("id", "")
        caption = self.params.get("caption", "")

        # Отправляем голосовое сообщение и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_voice(
            voice_id,
            caption=caption,
            reply_markup=await self.create_keyboard(self.params)
        )


class MediaGroupHandler(MediaHandler):
    async def send(self):
        media_items = self.params.get("media", [])
        media_group = [
            InputMediaPhoto(media=item['media']) if item['type'] == "photo" else InputMediaVideo(media=item['media'])
            for item in media_items]

        # Отправляем группу медиа и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer_media_group(
            media_group,
            caption=self.params.get("caption", "")
        )


class ButtonHandler(ScenarioHandler):
    def __init__(self, message: Message, params: dict, state: FSMContext, config):
        super().__init__(message, state, config)
        self.message = message
        self.params = params
        self.sent_message = None  # Сохраняем объект отправленного сообщения

    async def handle(self):
        """
        Обрабатывает кнопку в зависимости от типа действия:
        url, web_app, callback_data, execute_function.
        """
        button_type = self.params.get("type", "callback_data")

        if button_type == "url":
            await self.send_url()
        elif button_type == "web_app":
            await self.send_web_app()
        elif button_type == "callback_data":
            await self.send_callback()
        elif button_type == "execute_function":
            function_path = self.params.get("function_name")
            function_params = self.params.get("params", {})
            await self.execute_function(function_path=function_path, params=function_params)

    async def send_url(self):
        """
        Обработка кнопки с типом URL
        """
        url = self.params.get("url")
        text = self.params.get("text", "Перейти по ссылке")

        # Отправляем кнопку URL и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer(
            text,
            reply_markup=InlineKeyboardBuilder().add(InlineKeyboardButton(text=text, url=url)).as_markup()
        )

    async def send_web_app(self):
        """
        Обработка кнопки с типом Web App
        """
        web_app_url = self.params.get("web_app")
        text = self.params.get("text", "Открыть приложение")

        # Отправляем кнопку Web App и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer(
            text,
            reply_markup=InlineKeyboardBuilder().add(
                InlineKeyboardButton(text=text, web_app=WebAppInfo(url=web_app_url))).as_markup()
        )

    async def send_callback(self):
        """
        Обработка кнопки с типом callback_data
        """
        callback_data = self.params.get("callback_data")
        text = self.params.get("text", "Нажмите кнопку")

        # Отправляем кнопку с callback_data и сохраняем отправленное сообщение
        self.sent_message = await self.message.answer(
            text,
            reply_markup=InlineKeyboardBuilder().add(
                InlineKeyboardButton(text=text, callback_data=callback_data)).as_markup()
        )