from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from openpyxl import Workbook

def save_to_excel(data, filename="output.xlsx"):
    """
    Сохраняет список пользователей в Excel-файл.

    :param data: Список словарей с ключами 'user' и 'is_paid'.
    :param filename: Имя сохраняемого файла.
    """
    wb = Workbook()
    ws = wb.active

    # Заголовки
    headers = ["ID", "Имя", "Username", "Deeplink", "Покупка", "Premium", "Урок", "Дата захода"]
    ws.append(headers)

    # Данные
    for item in data:
        user = item["user"]
        is_paid = item["is_paid"]
        lesson_number = item["lesson_number"]

        row = [
            user.id,
            user.full_name if user.full_name else "—",
            "—" if not user.username else f"@{user.username}",
            user.deeplink or "—",
            "✅" if is_paid else "❌",
            "✅" if user.is_premium is True else "❌" if user.is_premium is False else "-",
            lesson_number,
            user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "—",
        ]
        ws.append(row)

    wb.save(filename)
    print(f"Файл сохранён как '{filename}'")


async def process_mailing_data(message: Message, state: FSMContext) -> bool:
    content_type = None
    content = message.text or message.caption
    file_id = None

    if message.text:
        content_type = 'text'

    elif message.animation:
        content_type = 'animation'
        file_id = message.animation.file_id
        content = message.caption

    elif message.audio:
        content_type = 'audio'
        file_id = message.audio.file_id
        content = message.caption

    elif message.document:
        content_type = 'document'
        file_id = message.document.file_id
        content = message.caption

    elif message.photo:
        content_type = 'photo'
        file_id = message.photo[-1].file_id
        content = message.caption

    elif message.sticker:
        content_type = 'sticker'
        file_id = message.sticker.file_id

    elif message.story:
        content_type = 'story'
        file_id = message.story.file_id

    elif message.video:
        content_type = 'video'
        file_id = message.video.file_id
        content = message.caption

    elif message.video_note:
        content_type = 'video_note'
        file_id = message.video_note.file_id

    elif message.voice:
        content_type = 'voice'
        file_id = message.voice.file_id

    else:
        return False

    await state.update_data(
        content_type=content_type,
        content=content,
        file_id=file_id
    )

    return True
