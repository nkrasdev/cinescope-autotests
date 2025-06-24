import logging
from urllib.parse import urljoin

import requests

from tests.constants import (LOGIN_ENDPOINT, ADMIN_EMAIL, ADMIN_PASSWORD, BASE_AUTH_URL)

class AuthAPI:

    def __init__(self, session: requests.Session) -> None:
        self.session: requests.Session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    def login(self, email: str = ADMIN_EMAIL, password: str = ADMIN_PASSWORD, expected_status: int = 200) -> requests.Response:
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