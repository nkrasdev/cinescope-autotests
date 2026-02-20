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
from tests.constants.log_messages import LogMessages
from tests.models.response_models import ErrorResponse, LoginResponse
from tests.models.user_models import User
from tests.request.custom_requester import CustomRequester

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

        self.logger.info(LogMessages.Auth.ATTEMPT_LOGIN.format(email))
        payload = {"email": email, "password": password}
        response = self.post(LOGIN_ENDPOINT, json=payload, expected_status=expected_status)
        if response.ok:
            login_response = LoginResponse.model_validate(response.json())
            self.session.headers["Authorization"] = f"Bearer {login_response.access_token}"
            self.logger.info(LogMessages.Auth.LOGIN_SUCCESS.format(email))
            return login_response

        error_response = ErrorResponse.model_validate(response.json())
        self.logger.error(f"Ошибка логина для {email}: {error_response.message} (status: {error_response.statusCode})")
        return error_response

    def register(self, user_data: dict, expected_status: int = 201) -> User | ErrorResponse:
        email = user_data.get("email", "N/A")
        self.logger.info(f"Попытка регистрации пользователя {email}")
        response = self.post(REGISTER_ENDPOINT, json=user_data, expected_status=expected_status)
        if response.ok:
            user = User.model_validate(response.json())
            self.logger.info(f"Пользователь {user.email} успешно зарегистрирован.")
            return user

        error_response = ErrorResponse.model_validate(response.json())
        self.logger.error(
            f"Ошибка регистрации для {email}: {error_response.message} (status: {error_response.statusCode})"
        )
        return error_response

    def logout(self, expected_status: int = 200) -> LogoutApiResponse:
        self.logger.info("Попытка выхода из системы (logout)")
        response = self.get(LOGOUT_ENDPOINT, expected_status=expected_status)
        if response.ok:
            self.logger.info("Выход из системы выполнен успешно")
            try:
                result: dict[str, Any] = response.json()
            except ValueError:
                result = {"message": response.text}
            return result
        self.logger.error(f"Ошибка выхода из системы: status {response.status_code}")
        return ErrorResponse.model_validate(response.json())

    def refresh_token(self, expected_status: int = 200) -> RefreshTokenApiResponse:
        self.logger.info("Попытка обновления токенов")
        response = self.get(REFRESH_ENDPOINT, expected_status=expected_status)
        if response.ok:
            self.logger.info("Токены успешно обновлены")
            result: dict[str, Any] = response.json()
            return result
        self.logger.error(f"Ошибка обновления токенов: status {response.status_code}")
        return ErrorResponse.model_validate(response.json())

    def confirm_email(self, token: str, expected_status: int = 200) -> ConfirmEmailApiResponse:
        self.logger.info("Попытка подтверждения email")
        response = self.get(f"{CONFIRM_ENDPOINT}/{token}", expected_status=expected_status)
        if response.ok:
            result: dict[str, Any] = response.json()
            return result
        return ErrorResponse.model_validate(response.json())
