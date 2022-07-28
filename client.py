"""
Необходимо реализовать клиент на Python к Cloudpayments API.
В рамках задачи необходимо реализовать оплату по криптограмме (метод charge).
Предполагается, что платежи будут проходить только по токену Yandex Pay.

Требования:

Реализовать аутентификацию запросов
Архитектура должна позволять добавлять остальные методы API.
Рекомендуется использовать python >3.10, marshmallow, marshmallow_dataclass, aiohttp >3.8
Реализация должна наследовать абстрактный класс AbstractInteractionClient.
"""


"""
ВОПРОСЫ:

1) вот здесь непонятный момент:

    "Предполагается, что платежи будут проходить только по токену Yandex Pay."

в документации Yandex Pay - "платежи через API"

    вот здесь: https://developers.cloudpayments.ru/#platezhi-cherez-api-cloudpayments

описано, что нужно получить от Yandex Pay Web SDK Token и передавать его в
запросе.

Сразу следом там же следует пример где передается в запросе не параметр
Token, а параметр CardCryptogramPacket, очевидно также сформированный Yandex
Pay Web SDK, а Token в примере нет.

и в самом задании указано реализовать оплату по криптограмме (т.е. вроде бы с
использованием данных CardCryptogramPacket), но следом уточняется, что "платежи
будут проходить только по токену Yandex Pay".

Оплата по токену указанная в документации это вроде бы отдельный случай (идет
уже после оплаты по криптограмме, токен тогда получен в ответе):
https://developers.cloudpayments.ru/#oplata-po-tokenu-rekarring

И там разные методы /charge для этих случаев.

Т.е. не очень понятно что нужно точно. Или разные случаи?

2) ответ https://developers.cloudpayments.ru/#obrabotka-3-d-secure нужно обрабатывать в тестовом задании?
или только метод charge?

КОММЕНТАРИИ

тестирования API как такового не делал (нет аккаунта CloudPayments)

задействовал сейчас в тестах ответы с сайта как мок-ответы endpoint-ов

я так понимаю marshmallow стоит использовать для валидации разных ожидаемых
ответов от CloudPayments, но это может для полноценной работы с API задача
"""

import base64
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from abstract_client import AbstractInteractionClient, InteractionResponseError
from aiohttp import ClientResponse, TCPConnector

logger = logging.getLogger("CloudPaymentsClient")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# create console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# create file handler for logger
fh = RotatingFileHandler("client.log", maxBytes=5000000, backupCount=8)
fh.setFormatter(formatter)
logger.addHandler(fh)


class CloudPaymentsClient(AbstractInteractionClient):

    SERVICE = "CloudPayments"
    BASE_URL = "https://api.cloudpayments.ru/"

    def __init__(self, public_id, api_secret):
        super().__init__()

        self.public_id = public_id
        self.api_secret = api_secret

        self.CONNECTOR = TCPConnector(limit=30)

        tokens = f"{self.public_id}:{self.api_secret}".encode("utf-8")
        base64string = base64.b64encode(tokens).decode("utf-8")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64string}",
        }

    async def charge(
        self,
        amount: float,
        card_cryptogram_packet: str,
        ip_address: str,
        invoice_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ClientResponse:
        """Performs payment using card cryptogram value

        :param amount: float
        :param card_cryptogram_packet: string (generated on the frontend)
        :param ip_address: string
        :param invoice_id: string
        :param description: string
        """

        self.headers["X-Request-ID"] = self._make_idempotent_request_id(
            amount=amount, card_cryptogram_packet=card_cryptogram_packet
        )

        json = {
            "Amount": amount,
            "IpAddress": ip_address,
            "CardCryptogramPacket": card_cryptogram_packet,
            "Currency": "RUB",
            "Description": description,
            "PublicId": self.public_id,
        }

        logger.debug(self.headers)
        logger.debug(self.endpoint_url("payments/charge"))
        logger.debug(json)

        try:
            res = await self.post(
                interaction_method="charge",
                url=self.endpoint_url("payments/charge"),
                headers=self.headers,
                json=json,
            )
        except InteractionResponseError as e:
            logger.exception(e)
            raise InteractionResponseError(
                status_code=e.status_code, method=e.method, service=e.service
            ) from e  # TODO: return something to handle error for the client
        except Exception as e:
            logger.exception(e)
            raise Exception from e  # return something to handle error for the client

        logger.debug(res)

        if not res["Success"]:
            return res  # TODO: something to handle error for the client. various cases

        return res

    def _make_idempotent_request_id(
        self, amount: float, card_cryptogram_packet: str
    ) -> str:
        h = hashlib.new("md5")
        h.update(f"{amount} {card_cryptogram_packet}".encode("utf-8"))
        return h.hexdigest()
