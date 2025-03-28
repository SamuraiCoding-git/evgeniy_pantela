import hashlib
import json

import requests
from sqlalchemy.util import await_only

from infrastructure.database.models import Product
from infrastructure.database.repo.requests import RequestsRepo


class Payment:
    def __init__(self, terminal_key: str, password: str, url: str = "https://securepay.tinkoff.ru"):
        self.terminal_key = terminal_key
        self.password = password
        self.url = url
        self.payment_data = None

    def _generate_token(self, request_data: dict) -> str:
        """
        Генерирует токен для MAPI (приватный метод).
        """
        filtered_data = {k: str(v) for k, v in request_data.items() if isinstance(v, (str, int, float))}
        filtered_data['Password'] = self.password
        sorted_items = sorted(filtered_data.items())
        concatenated_string = ''.join(value for _, value in sorted_items)
        return hashlib.sha256(concatenated_string.encode('utf-8')).hexdigest()

    def _send_post_request(self, method: str, data: dict) -> dict:
        """
        Отправляет POST-запрос к API (приватный метод).
        """
        full_url = f"{self.url}{method}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.post(full_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        except requests.exceptions.JSONDecodeError:
            return {"error": "Invalid JSON response"}

    async def create_payment(self, order_id: str, description: str, email: str, product: Product, repo: RequestsRepo) -> dict:
        """
        Создает новый платеж и сохраняет данные.
        """
        receipt = {
            "Email": email,
            "Taxation": "usn_income",
            "Items": [
                {
                    "Name": product.name,
                    "Price": product.price * 100,
                    "Quantity": 1,
                    "Amount": product.price * 100,
                    "Tax": "none",
                },
            ]
        }
        data = {
            "TerminalKey": self.terminal_key,
            "Amount": product.price * 100,
            "OrderId": order_id,
            "Description": description,
            "Receipt": receipt
        }
        data['Token'] = self._generate_token(data)
        response = self._send_post_request("/v2/Init", data)


        if response.get("Success"):
            await repo.purchases.update_purchase(
                int(order_id),
                int(response.get("PaymentId")),
                response.get('PaymentURL')
            )
            self.payment_data = response  # Сохранение данных платежа
            with open("payment_data.json", "w") as f:
                json.dump(response, f, indent=4)

        return response

    def get_payment_status(self, payment_id: str) -> bool:
        """
        Получает статус платежа и анализирует его.
        Возвращает True, если платеж успешен, иначе False.
        """
        data = {
            "TerminalKey": self.terminal_key,
            "PaymentId": payment_id
        }
        data['Token'] = self._generate_token(data)
        response = self._send_post_request("/v2/GetState", data)

        # Анализируем ответ API
        if response.get("Success") and response.get("ErrorCode") == "0":
            payments = response.get("Payments", [])
            if payments and isinstance(payments, list):
                payment_status = payments[0].get("Status", "")
                return payment_status == "CONFIRMED"
        return False

    @property
    def get_url(self):
        return self.payment_data['PaymentURL']
