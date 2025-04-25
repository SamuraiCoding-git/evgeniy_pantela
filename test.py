import requests

TOKEN = '8142455822:AAETdnZvpfeJTr6bzSbbWFS6oX41jmZkED4'  # Замените на ваш токен
API_URL = f'https://api.telegram.org/bot{TOKEN}/'


def get_updates():
    """Получаем обновления от бота."""
    url = f"{API_URL}getUpdates"
    response = requests.get(url)
    return response.json()


def get_media_from_last_message(updates, media_type):
    """Извлекаем media_id (photo, sticker, voice, video_note, audio, file) из последнего сообщения."""
    if 'result' in updates and len(updates['result']) > 0:
        last_message = updates['result'][-1]['message']

        if media_type == 'photo' and 'photo' in last_message:
            return last_message['photo'][-1]['file_id']

        elif media_type == 'video' and 'video' in last_message:
            return last_message['video']['file_id']

        elif media_type == 'sticker' and 'sticker' in last_message:
            return last_message['sticker']['file_id']

        elif media_type == 'voice' and 'voice' in last_message:
            return last_message['voice']['file_id']

        elif media_type == 'video_note' and 'video_note' in last_message:
            return last_message['video_note']['file_id']

        elif media_type == 'audio' and 'audio' in last_message:
            return last_message['audio']['file_id']

        elif media_type == 'file' and 'document' in last_message:
            return last_message['document']['file_id']

    return None


# Получаем обновления
updates = get_updates()

# Пример извлечения различных типов медиа из последнего сообщения
photo_id = get_media_from_last_message(updates, 'photo')
if photo_id:
    print(f"Получен file_id последней фотографии: {photo_id}")
else:
    print("Фото не найдено в последнем сообщении.")

video_id = get_media_from_last_message(updates, 'video')
if video_id:
    print(f"Получен file_id последней видео: {video_id}")
else:
    print("Видео не найдено в последнем сообщении.")

sticker_id = get_media_from_last_message(updates, 'sticker')
if sticker_id:
    print(f"Получен file_id последнего стикера: {sticker_id}")
else:
    print("Стикер не найден в последнем сообщении.")

voice_id = get_media_from_last_message(updates, 'voice')
if voice_id:
    print(f"Получен file_id последнего голосового сообщения: {voice_id}")
else:
    print("Голосовое сообщение не найдено в последнем сообщении.")

video_note_id = get_media_from_last_message(updates, 'video_note')
if video_note_id:
    print(f"Получен file_id последней видеозаметки: {video_note_id}")
else:
    print("Видеозаметка не найдена в последнем сообщении.")

audio_id = get_media_from_last_message(updates, 'audio')
if audio_id:
    print(f"Получен file_id последнего аудиофайла: {audio_id}")
else:
    print("Аудиофайл не найден в последнем сообщении.")

file_id = get_media_from_last_message(updates, 'file')
if file_id:
    print(f"Получен file_id последнего файла: {file_id}")
else:
    print("Файл не найден в последнем сообщении.")