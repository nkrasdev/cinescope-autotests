import logging
from collections.abc import Mapping
from typing import Any

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
    def login(
        self,
        email: str | None = ADMIN_EMAIL,
        password: str | None = ADMIN_PASSWORD,
        expected_status: int = 201,
    ) -> LoginApiResponse:
        if not email or not password:
            raise ValueError("ADMIN_EMAIL и ADMIN_PASSWORD должны быть указаны в .env file")

        log_event(self.logger, "auth", "login_attempt", email=email)
        credentials_payload = {"email": email, "password": password}
        response = self.post(LOGIN_ENDPOINT, json=credentials_payload, expected_status=expected_status)
        if response.ok:
            login_response = LoginResponse.model_validate(response.json())
            self.session.headers["Authorization"] = f"Bearer {login_response.access_token}"
            log_event(self.logger, "auth", "login_success", email=email)
            return login_response

        return self.parse_and_log_error(
            response,
            domain="auth",
            action="login_failed",
            level=logging.ERROR,
            email=email,
        )

    def register(self, user_data: Mapping[str, Any], expected_status: int = 201) -> RegisterApiResponse:
        email = user_data.get("email", "N/A")
        log_event(self.logger, "auth", "register_attempt", email=email)
        response = self.post(REGISTER_ENDPOINT, json=user_data, expected_status=expected_status)
        if response.ok:
            user = User.model_validate(response.json())
            log_event(self.logger, "auth", "register_success", email=user.email, user_id=user.id)
            return user

        return self.parse_and_log_error(
            response,
            domain="auth",
            action="register_failed",
            level=logging.ERROR,
            email=email,
        )

    def logout(self, expected_status: int = 200) -> LogoutApiResponse:
        log_event(self.logger, "auth", "logout_attempt")
        response = self.get(LOGOUT_ENDPOINT, expected_status=expected_status)
        if response.ok:
            log_event(self.logger, "auth", "logout_success")
            try:
                response_payload: dict[str, Any] = response.json()
            except ValueError:
                response_payload = {"message": response.text}
            return response_payload
        return self.parse_and_log_error(response, domain="auth", action="logout_failed", level=logging.ERROR)

    def refresh_token(self, expected_status: int = 201) -> RefreshTokenApiResponse:
        log_event(self.logger, "auth", "refresh_attempt")
        response = self.get(REFRESH_ENDPOINT, expected_status=expected_status)
        if response.ok:
            log_event(self.logger, "auth", "refresh_success")
            response_payload: dict[str, Any] = response.json()
            return response_payload
        return self.parse_and_log_error(response, domain="auth", action="refresh_failed", level=logging.ERROR)

    def confirm_email(self, token: str, expected_status: int = 200) -> ConfirmEmailApiResponse:
        log_event(self.logger, "auth", "confirm_email_attempt", token=token)
        response = self.get(
            f"{CONFIRM_ENDPOINT}/{token}",
            expected_status=expected_status,
            redact_url_path=True,
        )
        if response.ok:
            log_event(self.logger, "auth", "confirm_email_success")
            response_payload: dict[str, Any] = response.json()
            return response_payload
        return self.parse_and_log_error(response, domain="auth", action="confirm_email_failed", level=logging.WARNING)
