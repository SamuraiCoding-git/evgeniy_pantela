import importlib
import inspect

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    URLInputFile,
    InputMediaPhoto,
    InputMediaVideo
)
from aiogram.exceptions import TelegramBadRequest


async def send_media(message, media_type: str, params: dict, state):
    """
    Универсальная отправка медиа и возврат отправленного сообщения для дальнейшего редактирования.
    """
    media_senders = {
        "send_video": message.answer_video,
        "send_audio": message.answer_audio,
        "send_document": message.answer_document,
        "send_photo": message.answer_photo,
        "send_voice": message.answer_voice,
        "send_video_note": message.answer_video_note,
        "send_sticker": message.answer_sticker,
    }

    if media_type == "send_media_group":
        media_items = params.get("media", [])
        media_group = [
            InputMediaPhoto(media=item["media"]) if item["type"] == "photo" else InputMediaVideo(media=item["media"])
            for item in media_items
        ]
        return await message.answer_media_group(media_group)

    sender = media_senders.get(media_type)
    if not sender:
        raise ValueError(f"No sender for media type: {media_type}")

    media_content = params.get(media_type.split("_")[-1], {})
    file_id_or_url = media_content.get("id") or URLInputFile(media_content.get("url"))
    caption = params.get("caption")
    keyboard = await build_keyboard(params.get("keyboard", []))

    try:
        sent_message = await sender(file_id_or_url, caption=caption, reply_markup=keyboard)
        return sent_message
    except TelegramBadRequest as e:
        raise ValueError(f"Failed to send {media_type}: {e}")


async def build_keyboard(keyboard_data, state=None):
    if not keyboard_data:
        return None

    if isinstance(keyboard_data, str):
        try:
            module = importlib.import_module("tgbot.keyboards.inline")
            keyboard_obj = getattr(module, keyboard_data)

            # 🛠️ Если это функция — вызываем!
            if inspect.isfunction(keyboard_obj):
                keyboard_obj = keyboard_obj()

            return keyboard_obj
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Keyboard '{keyboard_data}' not found: {e}")


    keyboard = []
    for row in keyboard_data:
        button_row = []
        for button in row:
            btn_type = button.get("type", "callback_data")
            text = button.get("text", "Button")

            if btn_type == "url":
                button_row.append(InlineKeyboardButton(text=text, url=button.get("url")))
            elif btn_type == "web_app":
                button_row.append(InlineKeyboardButton(text=text, web_app=WebAppInfo(url=button.get("web_app"))))
            elif btn_type == "execute_function":
                callback_id = button.get("callback_id")
                if not callback_id:
                    raise ValueError("Button with type 'execute_function' must have 'callback_id'")
                button_row.append(InlineKeyboardButton(text=text, callback_data=f"callback:{callback_id}"))
            else:
                button_row.append(InlineKeyboardButton(text=text, callback_data=button.get("callback_data")))
        keyboard.append(button_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def handle_callback(self, callback_id: str):
    """
    Обрабатывает callback_id по нажатию на кнопку.
    """
    callback_actions = self.callbacks.get(callback_id)
    if not callback_actions:
        await self.message.answer("Произошла ошибка: действие не найдено.")
        return

    for action in callback_actions:
        function_name = action.get("function_name")
        params = action.get("params", {})

        if function_name.startswith("send_"):
            await self.handle_send_media(function_name, params)
        elif function_name == "send_text":
            await self.handle_send_text(params)
        else:
            await self.execute_function(function_name, params)