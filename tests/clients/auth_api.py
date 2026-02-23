import logging
from typing import Any

import requests

from tests.constants.endpoints import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    CONFIRM_ENDPOINT,
    LOGIN_ENDPOINT,
    LOGOUT_ENDPOINT,
    REFRESH_ENDPOINT,
    REGISTER_ENDPOINT,
)
from tests.models.response_models import ErrorResponse, LoginResponse
from tests.models.user_models import User
from tests.request.custom_requester import CustomRequester
from tests.utils.logging_utils import log_event

type LoginApiResponse = LoginResponse | ErrorResponse
type RegisterApiResponse = User | ErrorResponse
type LogoutApiResponse = dict[str, Any] | ErrorResponse
type RefreshTokenApiResponse = dict[str, Any] | ErrorResponse
type ConfirmEmailApiResponse = dict[str, Any] | ErrorResponse


class AuthAPI(CustomRequester):
    def __init__(self, session: requests.Session, base_url: str) -> None:
        super().__init__(session, base_url=base_url)
        self.logger = logging.getLogger(self.__class__.__name__)

    def login(
        self,
        email: str | None = ADMIN_EMAIL,
        password: str | None = ADMIN_PASSWORD,
        expected_status: int = 200,
    ) -> LoginApiResponse:
        if not email or not password:
            raise ValueError("ADMIN_EMAIL и ADMIN_PASSWORD должны быть указаны в .env file")

        log_event(self.logger, "auth", "login_attempt", email=email)
        payload = {"email": email, "password": password}
        response = self.post(LOGIN_ENDPOINT, json=payload, expected_status=expected_status)
        if response.ok:
            login_response = LoginResponse.model_validate(response.json())
            self.session.headers["Authorization"] = f"Bearer {login_response.access_token}"
            log_event(self.logger, "auth", "login_success", email=email)
            return login_response

        error_response = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "auth",
            "login_failed",
            level=logging.ERROR,
            email=email,
            status_code=error_response.statusCode,
            error=error_response.message,
        )
        return error_response

    def register(self, user_data: dict, expected_status: int = 201) -> User | ErrorResponse:
        email = user_data.get("email", "N/A")
        log_event(self.logger, "auth", "register_attempt", email=email)
        response = self.post(REGISTER_ENDPOINT, json=user_data, expected_status=expected_status)
        if response.ok:
            user = User.model_validate(response.json())
            log_event(self.logger, "auth", "register_success", email=user.email, user_id=user.id)
            return user

        error_response = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "auth",
            "register_failed",
            level=logging.ERROR,
            email=email,
            status_code=error_response.statusCode,
            error=error_response.message,
        )
        return error_response

    def logout(self, expected_status: int = 200) -> LogoutApiResponse:
        log_event(self.logger, "auth", "logout_attempt")
        response = self.get(LOGOUT_ENDPOINT, expected_status=expected_status)
        if response.ok:
            log_event(self.logger, "auth", "logout_success")
            try:
                result: dict[str, Any] = response.json()
            except ValueError:
                result = {"message": response.text}
            return result
        log_event(self.logger, "auth", "logout_failed", level=logging.ERROR, status_code=response.status_code)
        return ErrorResponse.model_validate(response.json())

    def refresh_token(self, expected_status: int = 200) -> RefreshTokenApiResponse:
        log_event(self.logger, "auth", "refresh_attempt")
        response = self.get(REFRESH_ENDPOINT, expected_status=expected_status)
        if response.ok:
            log_event(self.logger, "auth", "refresh_success")
            result: dict[str, Any] = response.json()
            return result
        log_event(self.logger, "auth", "refresh_failed", level=logging.ERROR, status_code=response.status_code)
        return ErrorResponse.model_validate(response.json())

    def confirm_email(self, token: str, expected_status: int = 200) -> ConfirmEmailApiResponse:
        log_event(self.logger, "auth", "confirm_email_attempt", token=token)
        response = self.get(f"{CONFIRM_ENDPOINT}/{token}", expected_status=expected_status)
        if response.ok:
            log_event(self.logger, "auth", "confirm_email_success")
            result: dict[str, Any] = response.json()
            return result
        log_event(self.logger, "auth", "confirm_email_failed", level=logging.WARNING, status_code=response.status_code)
        return ErrorResponse.model_validate(response.json())
