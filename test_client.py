import json

import aiohttp
import aresponses
import pytest
from abstract_client import InteractionResponseError
from client import CloudPaymentsClient


@pytest.fixture
def response_fail1():
    return {
        "Success": False,
        "Message": "Amount is required"
    }


@pytest.fixture
def response_fail2():
    return {
        "Model": {
            "ReasonCode": 5051,
            "PublicId": "pk_**********************************",
            "TerminalUrl": "http://test.test",
            "TransactionId": 891583633,
            "Amount": 10,
            "Currency": "RUB",
            "CurrencyCode": 0,
            "PaymentAmount": 10,
            "PaymentCurrency": "RUB",
            "PaymentCurrencyCode": 0,
            "InvoiceId": "1234567",
            "AccountId": "user_x",
            "Email": None,
            "Description": "Оплата товаров в example.com",
            "JsonData": None,
            "CreatedDate": "/Date(1635154784619)/",
            "PayoutDate": None,
            "PayoutDateIso": None,
            "PayoutAmount": None,
            "CreatedDateIso": "2021-10-25T09:39:44",
            "AuthDate": None,
            "AuthDateIso": None,
            "ConfirmDate": None,
            "ConfirmDateIso": None,
            "AuthCode": None,
            "TestMode": True,
            "Rrn": None,
            "OriginalTransactionId": None,
            "FallBackScenarioDeclinedTransactionId": None,
            "IpAddress": "123.123.123.123",
            "IpCountry": "CN",
            "IpCity": "Beijing",
            "IpRegion": "Beijing",
            "IpDistrict": "Beijing",
            "IpLatitude": 39.9289,
            "IpLongitude": 116.3883,
            "CardFirstSix": "400005",
            "CardLastFour": "5556",
            "CardExpDate": "12/25",
            "CardType": "Visa",
            "CardProduct": None,
            "CardCategory": None,
            "EscrowAccumulationId": None,
            "IssuerBankCountry": "US",
            "Issuer": "ITS Bank",
            "CardTypeCode": 0,
            "Status": "Declined",
            "StatusCode": 5,
            "CultureName": "ru",
            "Reason": "InsufficientFunds",
            "CardHolderMessage": "Недостаточно средств на карте",
            "Type": 0,
            "Refunded": False,
            "Name": "CARDHOLDER NAME",
            "Token": "tk_255c42192323f2e09ea17635302c3",
            "SubscriptionId": None,
            "GatewayName": "Test",
            "ApplePay": False,
            "AndroidPay": False,
            "WalletType": "",
            "TotalFee": 0
        },
        "Success": False,
        "Message": None
    }


@pytest.fixture
def response_success():
    return {
        "Model": {
            "ReasonCode": 0,
            "PublicId": "pk_********************************",
            "TerminalUrl": "http://test.test",
            "TransactionId": 891510444,
            "Amount": 10,
            "Currency": "RUB",
            "CurrencyCode": 0,
            "PaymentAmount": 10,
            "PaymentCurrency": "RUB",
            "PaymentCurrencyCode": 0,
            "InvoiceId": "1234567",
            "AccountId": "user_x",
            "Email": None,
            "Description": "Оплата товаров в example.com",
            "JsonData": None,
            "CreatedDate": "/Date(1635150224630)/",
            "PayoutDate": None,
            "PayoutDateIso": None,
            "PayoutAmount": None,
            "CreatedDateIso": "2021-10-25T08:23:44",
            "AuthDate": "/Date(1635150224739)/",
            "AuthDateIso": "2021-10-25T08:23:44",
            "ConfirmDate": None,
            "ConfirmDateIso": None,
            "AuthCode": "A1B2C3",
            "TestMode": True,
            "Rrn": None,
            "OriginalTransactionId": None,
            "FallBackScenarioDeclinedTransactionId": None,
            "IpAddress": "123.123.123.123",
            "IpCountry": "CN",
            "IpCity": "Beijing",
            "IpRegion": "Beijing",
            "IpDistrict": "Beijing",
            "IpLatitude": 39.9289,
            "IpLongitude": 116.3883,
            "CardFirstSix": "411111",
            "CardLastFour": "1111",
            "CardExpDate": "11/25",
            "CardType": "Visa",
            "CardProduct": "C",
            "CardCategory": "Visa Signature (Signature)",
            "EscrowAccumulationId": None,
            "IssuerBankCountry": "RU",
            "Issuer": "CloudPayments",
            "CardTypeCode": 0,
            "Status": "Authorized",
            "StatusCode": 2,
            "CultureName": "ru",
            "Reason": "Approved",
            "CardHolderMessage": "Оплата успешно проведена",
            "Type": 0,
            "Refunded": False,
            "Name": "CARDHOLDER NAME",
            "Token": "0a0afb77-8f41-4de2-9524-1057f9695303",
            "SubscriptionId": None,
            "GatewayName": "Test",
            "ApplePay": False,
            "AndroidPay": False,
            "WalletType": "",
            "TotalFee": 0
        },
        "Success": True,
        "Message": None
    }


class TestCloudPaymentsClient:

    PUBLIC_ID = 'test_api_00000000000000000000002'
    API_SECRET = '9272c64f-d49f-4bbc-83e8-1753496b4e3b'

    # taken from https://developers.cloudpayments.ru/#platezhi-cherez-api-cloudpayments
    CARD_CRYPTOGRAM_PACKET = (
        "\"{\\\"type\\\":\\\"Yandex\\\",\\\"signedMessage\\\":\\\"{\\\\\\\"",
        "encryptedMessage\\\\\\\":\\\\\\\"xqpAiS2L71BZNgH514AQDwOVawJF4gHXF",
        "8P+ECIFRqFHlDMRtxHsO9hNQSeegSssRdDMlBIyOObY5dqI3iwX99UKYP6qFD+tKEY",
        "JQkUdiKyhZCwgUsVdHBlFQA+iiXVLf7DZ5WCIaHjpl4mckrGeDg4XGDIX4FB0BorLq",
        "ocbDLcl0JZi2zzkNtn9FDLPSAs1qbTEMdb3TAS0iDAIkuAy5DGJ3+4Av9PWvIllW4L",
        "RdQ34rR8MPszJxq9Xagw/jeKUglyUERQgi5cnVWIB992yPh9UFgNuCQBc+JWLMzuOI",
        "KKxFiVK6VBSsuHpDWrSZqMolN6PIeNvETxQ34g+O/u4KiwWd3IG/pb5e0FYbzn/gWz",
        "lDSPsqNSuB713qZDHCI7eFB7h7iPTdk/Wd78Vv7Vlg4oVQdMWCbgSjtWDamKeq/OMi",
        "VDW5j36CebRQWxB8/XFj4nAInHIjoUUKsEQ5gf00n9/48RUNVCbRr6qykvsfnD0XP5",
        "V4OJOeIhAZN2CAgGxgrGC5MibfjAf+D/EnunHwOvtmI6KQAsGv9QgrRC8sxTeyk7OT",
        "9vUCzK2DIRDYyCtvloGalRq1PRdJWQX\\\\\\\",\\\\\\\"tag\\\\\\\":\\\\\\",
        "\"LTx6/HA9iWaZwbYaFN1j9aDOPp2PBlR2iBMUBQ7zyUg=\\\\\\\",\\\\\\\"eph",
        "emeralPublicKey\\\\\\\":\\\\\\\"BHHBcT4SvFgxMK14Oz3/dk/uiCL2m4jeTF",
        "DEcoYHXt5gAz2wFVEnvRD4fHArkbIOcry9nlUYHWgT4GicEl9qkXY=\\\\\\\"}\\",
        "\",\\\"protocolVersion\\\":\\\"ECv2\\\",\\\"signature\\\":\\\"MEU",
        "CICyyzWnCEf2iHlUszDzvbAx/qk/sLmbTaOWPVEq1hr29AiEA0lfZ85pCofYhxVX9",
        "71Xtshysawi7+KEe8ZpPVlV/Md4=\\\",\\\"intermediateSigningKey\\\":{",
        "\\\"signedKey\\\":\\\"{\\\\\\\"keyValue\\\\\\\":\\\\\\\"MFkwEwYHK",
        "oZIzj0CAQYIKoZIzj0DAQcDQgAEqYNePt6BPgCv5JxfO9dF2vrSqmnp4Mhe/vF+XO",
        "+Devbs6/KVpVVoTD8LLcAo4TZh6IuODVnVpHrTObhg3HJVJA==\\\\\\\",\\\\\\",
        "\"keyExpiration\\\\\\\":\\\\\\\"1764950892000\\\\\\\"}\\\",\\\"si",
        "gnatures\\\":[\\\"MEQCIDRslMW7wNZbpqVw/dD7hDQh30hGhqfjfWTBvc7zAYJ",
        "SAiAGAvjAslA2AxwdAEuOfacFr6DaE5yiiUuUtM6DUreZYg==\\\"]}}\""
    )

    @pytest.mark.asyncio
    async def test_payment_unauthorized(self):

        client = CloudPaymentsClient(
            public_id=self.PUBLIC_ID,
            api_secret=self.API_SECRET
        )

        with pytest.raises(InteractionResponseError):
            await client.charge(
                amount=1000.0,
                ip_address='11.62.215.130',
                card_cryptogram_packet=self.CARD_CRYPTOGRAM_PACKET,
                description='Покупка по заказу 123456',
            )

    @pytest.mark.asyncio
    async def test_payment_success(self, aresponses, response_success):

        aresponses.add(
            "api.cloudpayments.ru",
            "/payments/charge",
            "POST",
            response=response_success
        )

        client = CloudPaymentsClient(
            public_id=self.PUBLIC_ID,
            api_secret=self.API_SECRET
        )

        resp = await client.charge(
            amount=1000.0,
            ip_address='228.216.41.16',
            card_cryptogram_packet=self.CARD_CRYPTOGRAM_PACKET,
            description='Покупка по заказу 123456',
        )

        assert resp == response_success
        aresponses.assert_plan_strictly_followed()

    @pytest.mark.asyncio
    async def test_payment_fail(self, aresponses, response_fail1):

        aresponses.add(
            "api.cloudpayments.ru",
            "/payments/charge",
            "POST",
            response=response_fail1
        )

        client = CloudPaymentsClient(
            public_id=self.PUBLIC_ID,
            api_secret=self.API_SECRET
        )

        resp = await client.charge(
            amount=0,
            ip_address='130.209.9.62',
            card_cryptogram_packet=self.CARD_CRYPTOGRAM_PACKET,
            description='Покупка по заказу 123456',
        )

        assert resp == response_fail1
        aresponses.assert_plan_strictly_followed()

    @pytest.mark.asyncio
    async def test_payment_fail_2(self, aresponses, response_fail2):

        aresponses.add(
            "api.cloudpayments.ru",
            "/payments/charge",
            "POST",
            response=response_fail2
        )

        client = CloudPaymentsClient(
            public_id=self.PUBLIC_ID,
            api_secret=self.API_SECRET
        )

        resp = await client.charge(
            amount=12345.6,
            ip_address='130.209.9.62',
            card_cryptogram_packet=self.CARD_CRYPTOGRAM_PACKET,
            description='Покупка по заказу 123456',
        )

        assert resp == response_fail2
        aresponses.assert_plan_strictly_followed()
