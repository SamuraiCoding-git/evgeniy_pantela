import uuid
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
    keyboard = await build_keyboard(params.get("keyboard", []), state)

    try:
        sent_message = await sender(file_id_or_url, caption=caption, reply_markup=keyboard)
        return sent_message
    except TelegramBadRequest as e:
        raise ValueError(f"Failed to send {media_type}: {e}")


async def build_keyboard(keyboard_data: list, state) -> InlineKeyboardMarkup | None:
    """
    Построение инлайн-клавиатуры с поддержкой execute_function через FSMContext.
    """
    if not keyboard_data:
        return None

    keyboard = []
    for row in keyboard_data:
        button_row = []
        for button in row:
            btn_type = button.get("type", "callback_data")
            text = button.get("text", "Button")

            if btn_type == "url":
                button_row.append(InlineKeyboardButton(
                    text=text,
                    url=button.get("url")
                ))
            elif btn_type == "web_app":
                button_row.append(InlineKeyboardButton(
                    text=text,
                    web_app=WebAppInfo(url=button.get("web_app"))
                ))
            elif btn_type == "execute_function":
                unique_id = str(uuid.uuid4())
                await state.update_data({unique_id: button.get("params", {}).get("functions", [])})
                button_row.append(InlineKeyboardButton(
                    text=text,
                    callback_data=f"execute_function:{unique_id}"
                ))
            else:  # обычная callback_data
                button_row.append(InlineKeyboardButton(
                    text=text,
                    callback_data=button.get("callback_data")
                ))

        keyboard.append(button_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)