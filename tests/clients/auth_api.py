import logging
import requests
from typing import Union
from tests.constants import (LOGIN_ENDPOINT, ADMIN_EMAIL, ADMIN_PASSWORD,
                             REGISTER_ENDPOINT, LOGOUT_ENDPOINT, REFRESH_ENDPOINT)
from tests.request.custom_requester import CustomRequester
from tests.models.auth import LoginResponse
from tests.models.user import User

class AuthAPI(CustomRequester):

    def __init__(self, session: requests.Session, base_url: str) -> None:
        super().__init__(session, base_url=base_url)
        self.logger = logging.getLogger(self.__class__.__name__)

    def login(self, email: str | None = ADMIN_EMAIL, password: str | None = ADMIN_PASSWORD,
              expected_status: int = 200) -> Union[LoginResponse, requests.Response]:
        if not email or not password:
            raise ValueError("ADMIN_EMAIL и ADMIN_PASSWORD должны быть указаны в .env file")

        payload = {"email": email, "password": password}
        response = self.post(LOGIN_ENDPOINT, data=payload, expected_status=expected_status)
        if response.ok:
            login_response = LoginResponse.model_validate(response.json())
            self.session.headers["Authorization"] = f"Bearer {login_response.access_token}"
            self.logger.info("Логин выполнен.")
            return login_response
        return response

    def register(self, user_data: dict, expected_status: int = 201) -> Union[User, requests.Response]:
        response = self.post(REGISTER_ENDPOINT, data=user_data, expected_status=expected_status)
        if response.ok:
            return User.model_validate(response.json())
        return response

    def logout(self, expected_status: int = 200) -> requests.Response:
        return self.get(LOGOUT_ENDPOINT, expected_status=expected_status)

    def refresh_tokens(self, expected_status: int = 200) -> requests.Response:
        return self.get(REFRESH_ENDPOINT, expected_status=expected_status)