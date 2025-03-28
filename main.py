import hashlib
import time

import requests

def generate_mapi_token(request_data: dict, password: str) -> str:
    """
    Генерирует токен для MAPI.

    :param request_data: Словарь с параметрами запроса
    :param password: Пароль мерчанта
    :return: Строка с токеном
    """
    filtered_data = {k: str(v) for k, v in request_data.items() if isinstance(v, (str, int, float))}
    filtered_data['Password'] = password
    sorted_items = sorted(filtered_data.items())
    concatenated_string = ''.join(value for _, value in sorted_items)
    token = hashlib.sha256(concatenated_string.encode('utf-8')).hexdigest()
    return token

def send_post_request(url: str, method: str, data: dict) -> dict:
    """
    Отправляет POST-запрос к API MAPI.

    :param url: URL сервера
    :param method: Метод API
    :param data: Данные запроса
    :return: Ответ API в формате JSON
    """
    full_url = f"{url}{method}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'  # Добавлен заголовок
    }

    try:
        response = requests.post(full_url, json=data, headers=headers)
        response.raise_for_status()  # Вызывает исключение при ошибке HTTP (4xx, 5xx)

        print(f"Response status: {response.status_code}")  # Логирование статуса
        print(f"Response text: {response.text}")  # Логирование содержимого ответа

        return response.json()  # Преобразуем JSON-ответ

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {"error": str(e)}
    except requests.exceptions.JSONDecodeError:
        print("Ошибка декодирования JSON! Возможно, сервер вернул HTML или пустой ответ.")
        return {"error": "Invalid JSON response"}

url = "https://securepay.tinkoff.ru"
password = "$J_OSG2jkVlR*2Jw"

# Создание платежа
data = {
    "TerminalKey": "1742052542588",
    "Amount": 100,
    "OrderId": "21084",
    "Description": "Подарочная карта на 1000 рублей",
    "DATA": {
        "Email": "pantelaregist@yandex.ru"
    },
    "Receipt": {
        "Email": "pantelaregist@yandex.ru",
        "Taxation": "patent",
        "Items": [
            {
                "Name": "доступ в телеграмм канал",
                "Price": 100,
                "Quantity": 1,
                "Amount": 100,
                "Tax": "none"
            }
        ]
    }
}

data['Token'] = generate_mapi_token(data, password)
init_response = send_post_request(url, "/v2/Init", data)
print("Init Response:", init_response)