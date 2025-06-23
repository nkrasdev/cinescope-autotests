import logging
from urllib.parse import urljoin

import requests

from tests.constants import (LOGIN_ENDPOINT, ADMIN_EMAIL, ADMIN_PASSWORD, BASE_AUTH_URL,
                             REGISTER_ENDPOINT, LOGOUT_ENDPOINT, REFRESH_ENDPOINT)


class AuthAPI:

    def __init__(self, session: requests.Session) -> None:
        self.session: requests.Session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    def login(self, email: str = ADMIN_EMAIL, password: str = ADMIN_PASSWORD, expected_status: int = 200) -> requests.Response:
        """
        Выполняет вход в систему и устанавливает токен авторизации в сессию.
        """
        payload = {"email": email, "password": password}
        url = urljoin(BASE_AUTH_URL, LOGIN_ENDPOINT)

        response = self.session.post(url, json=payload)
        assert response.status_code == expected_status, \
            f"Unexpected status code: {response.status_code}, expected: {expected_status}"

        if response.ok:
            access_token = response.json()["accessToken"]
            self.session.headers["Authorization"] = f"Bearer {access_token}"
            self.logger.info("Login successful - new access token obtained.")

        return response

    def register(self, user_data: dict, expected_status: int = 201) -> requests.Response:
        """
        Регистрирует нового пользователя.
        """
        url = urljoin(BASE_AUTH_URL, REGISTER_ENDPOINT)
        response = self.session.post(url, json=user_data)
        assert response.status_code == expected_status, \
            f"Unexpected status code: {response.status_code}, expected: {expected_status}"
        return response

    def logout(self, expected_status: int = 200) -> requests.Response:
        """
        Выполняет выход из системы.
        """
        url = urljoin(BASE_AUTH_URL, LOGOUT_ENDPOINT)
        response = self.session.get(url)
        assert response.status_code == expected_status, \
            f"Unexpected status code: {response.status_code}, expected: {expected_status}"
        return response

    def refresh_tokens(self, expected_status: int = 200) -> requests.Response:
        """
        Обновляет access и refresh токены.
        """
        url = urljoin(BASE_AUTH_URL, REFRESH_ENDPOINT)
        response = self.session.get(url)
        assert response.status_code == expected_status, \
            f"Unexpected status code: {response.status_code}, expected: {expected_status}"
        return response