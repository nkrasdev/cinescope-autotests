import logging

import requests

from tests.constants.endpoints import USER_BY_ID_ENDPOINT, USER_BY_ID_OR_EMAIL_ENDPOINT, USERS_ENDPOINT
from tests.models.response_models import ErrorResponse, UsersListResponse
from tests.models.user_models import User
from tests.request.custom_requester import CustomRequester

type UsersListApiResponse = UsersListResponse | ErrorResponse
type UserApiResponse = User | ErrorResponse | None


class UsersAPI(CustomRequester):
    def __init__(self, session: requests.Session, base_url: str) -> None:
        super().__init__(session, base_url=base_url)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_user(self, user_data: dict, expected_status: int = 201) -> UserApiResponse:
        self.logger.info("Попытка создания пользователя")
        response = self.post(USERS_ENDPOINT, json=user_data, expected_status=expected_status)
        if response.ok:
            return User.model_validate(response.json())
        return ErrorResponse.model_validate(response.json())

    def get_user(self, id_or_email: str, expected_status: int = 200) -> UserApiResponse:
        self.logger.info(f"Попытка получения пользователя {id_or_email}")
        response = self.get(
            USER_BY_ID_OR_EMAIL_ENDPOINT.format(id_or_email=id_or_email), expected_status=expected_status
        )
        if response.ok:
            return User.model_validate(response.json())
        return ErrorResponse.model_validate(response.json())

    def get_users(self, params: dict | None = None, expected_status: int = 200) -> UsersListApiResponse:
        self.logger.info("Попытка получения списка пользователей")
        response = self.get(USERS_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            data = response.json()
            if isinstance(data, list):
                if not data:
                    return UsersListResponse(users=[], count=0, page=1, pageSize=0)
                if isinstance(data[0], dict) and "users" in data[0]:
                    data = data[0]
                else:
                    users = [User.model_validate(item) for item in data]
                    return UsersListResponse(users=users, count=len(users), page=1, pageSize=len(users))
            return UsersListResponse.model_validate(data)
        return ErrorResponse.model_validate(response.json())

    def edit_user(self, user_id: str, user_data: dict, expected_status: int = 200) -> UserApiResponse:
        self.logger.info(f"Попытка редактирования пользователя {user_id}")
        response = self.patch(
            USER_BY_ID_ENDPOINT.format(user_id=user_id), json=user_data, expected_status=expected_status
        )
        if response.ok:
            data = response.json()
            data.setdefault("id", user_id)
            return User.model_validate(data)
        return ErrorResponse.model_validate(response.json())

    def delete_user(self, user_id: str, expected_status: int = 200) -> UserApiResponse:
        self.logger.info(f"Попытка удаления пользователя {user_id}")
        response = self.delete(USER_BY_ID_ENDPOINT.format(user_id=user_id), expected_status=expected_status)
        if response.ok:
            if response.content:
                return User.model_validate(response.json())
            return None
        return ErrorResponse.model_validate(response.json())
