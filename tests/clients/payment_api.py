import logging

import requests

from tests.constants.endpoints import (
    PAYMENT_CREATE_ENDPOINT,
    PAYMENT_FIND_ALL_ENDPOINT,
    PAYMENT_USER_BY_ID_ENDPOINT,
    PAYMENT_USER_ENDPOINT,
)
from tests.models.payment_models import PaymentRegistryResponse, PaymentResponse, PaymentsListResponse
from tests.request.custom_requester import CustomRequester

type PaymentCreateResponse = PaymentRegistryResponse | requests.Response
type PaymentsResponse = list[PaymentResponse] | requests.Response
type PaymentsListApiResponse = PaymentsListResponse | requests.Response


class PaymentAPI(CustomRequester):
    def __init__(self, session: requests.Session, base_url: str) -> None:
        super().__init__(session, base_url=base_url)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_payment(self, payload: dict, expected_status: int = 201) -> PaymentCreateResponse:
        self.logger.info("Попытка создания платежа")
        response = self.post(PAYMENT_CREATE_ENDPOINT, json=payload, expected_status=expected_status)
        if response.ok:
            return PaymentRegistryResponse.model_validate(response.json())
        return response

    def get_current_user_payments(self, expected_status: int = 200) -> PaymentsResponse:
        self.logger.info("Попытка получения платежей текущего пользователя")
        response = self.get(PAYMENT_USER_ENDPOINT, expected_status=expected_status)
        if response.ok:
            return [PaymentResponse.model_validate(item) for item in response.json()]
        return response

    def get_user_payments(self, user_id: str, expected_status: int = 200) -> PaymentsResponse:
        self.logger.info(f"Попытка получения платежей пользователя {user_id}")
        response = self.get(PAYMENT_USER_BY_ID_ENDPOINT.format(user_id=user_id), expected_status=expected_status)
        if response.ok:
            return [PaymentResponse.model_validate(item) for item in response.json()]
        return response

    def get_all_payments(self, params: dict | None = None, expected_status: int = 200) -> PaymentsListApiResponse:
        self.logger.info("Попытка получения всех платежей")
        response = self.get(PAYMENT_FIND_ALL_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            return PaymentsListResponse.model_validate(response.json())
        return response
