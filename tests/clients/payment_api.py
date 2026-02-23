import logging

import requests

from tests.constants.endpoints import (
    PAYMENT_CREATE_ENDPOINT,
    PAYMENT_FIND_ALL_ENDPOINT,
    PAYMENT_USER_BY_ID_ENDPOINT,
    PAYMENT_USER_ENDPOINT,
)
from tests.models.payment_models import PaymentRegistryResponse, PaymentResponse, PaymentsListResponse, PaymentStatus
from tests.models.response_models import ErrorResponse
from tests.request.custom_requester import CustomRequester
from tests.utils.logging_utils import log_event

type PaymentCreateResponse = PaymentRegistryResponse | ErrorResponse
type PaymentsResponse = list[PaymentResponse] | ErrorResponse
type PaymentsListApiResponse = PaymentsListResponse | ErrorResponse


class PaymentAPI(CustomRequester):
    def __init__(self, session: requests.Session, base_url: str) -> None:
        super().__init__(session, base_url=base_url)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_payment(self, payload: dict, expected_status: int | None = 201) -> PaymentCreateResponse:
        log_event(self.logger, "payment", "create_attempt", movie_id=payload.get("movieId"))
        response = self.post(PAYMENT_CREATE_ENDPOINT, json=payload, expected_status=expected_status)
        if response.ok:
            payment = PaymentRegistryResponse.model_validate(response.json())
            log_event(self.logger, "payment", "create_success", status=payment.status.value)
            return payment
        body = response.json()
        payment_status = body.get("error", {}).get("status") if isinstance(body, dict) else None
        if isinstance(payment_status, str) and payment_status in PaymentStatus._value2member_map_:
            log_event(self.logger, "payment", "create_failed", level=logging.WARNING, status=payment_status)
            return PaymentRegistryResponse(status=PaymentStatus(payment_status))
        error = ErrorResponse.model_validate(body)
        log_event(
            self.logger,
            "payment",
            "create_failed",
            level=logging.ERROR,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_current_user_payments(self, expected_status: int = 200) -> PaymentsResponse:
        log_event(self.logger, "payment", "list_current_user_attempt")
        response = self.get(PAYMENT_USER_ENDPOINT, expected_status=expected_status)
        if response.ok:
            payments = [PaymentResponse.model_validate(item) for item in response.json()]
            log_event(self.logger, "payment", "list_current_user_success", count=len(payments))
            return payments
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "payment",
            "list_current_user_failed",
            level=logging.ERROR,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_user_payments(self, user_id: str, expected_status: int = 200) -> PaymentsResponse:
        log_event(self.logger, "payment", "list_user_attempt", user_id=user_id)
        response = self.get(PAYMENT_USER_BY_ID_ENDPOINT.format(user_id=user_id), expected_status=expected_status)
        if response.ok:
            payments = [PaymentResponse.model_validate(item) for item in response.json()]
            log_event(self.logger, "payment", "list_user_success", user_id=user_id, count=len(payments))
            return payments
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "payment",
            "list_user_failed",
            level=logging.ERROR,
            user_id=user_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_all_payments(self, params: dict | None = None, expected_status: int = 200) -> PaymentsListApiResponse:
        log_event(self.logger, "payment", "list_all_attempt", params=params or "default")
        response = self.get(PAYMENT_FIND_ALL_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            payments = PaymentsListResponse.model_validate(response.json())
            log_event(self.logger, "payment", "list_all_success", count=payments.count)
            return payments
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "payment",
            "list_all_failed",
            level=logging.ERROR,
            status_code=error.statusCode,
            error=error.message,
        )
        return error
