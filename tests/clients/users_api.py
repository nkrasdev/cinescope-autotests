import logging

import requests

from tests.constants.endpoints import USER_BY_ID_ENDPOINT, USER_BY_ID_OR_EMAIL_ENDPOINT, USERS_ENDPOINT
from tests.models.response_models import ErrorResponse, UsersListResponse
from tests.models.user_models import User
from tests.request.custom_requester import CustomRequester
from tests.utils.logging_utils import log_event

type UsersListApiResponse = UsersListResponse | ErrorResponse
type UserApiResponse = User | ErrorResponse | None


class UsersAPI(CustomRequester):
    def __init__(self, session: requests.Session, base_url: str) -> None:
        super().__init__(session, base_url=base_url)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_user(self, user_data: dict, expected_status: int = 201) -> UserApiResponse:
        log_event(self.logger, "user", "create_attempt", email=user_data.get("email"))
        response = self.post(USERS_ENDPOINT, json=user_data, expected_status=expected_status)
        if response.ok:
            user = User.model_validate(response.json())
            log_event(self.logger, "user", "create_success", user_id=user.id, email=user.email)
            return user
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "user",
            "create_failed",
            level=logging.ERROR,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_user(self, id_or_email: str, expected_status: int = 200) -> UserApiResponse:
        log_event(self.logger, "user", "get_attempt", id_or_email=id_or_email)
        response = self.get(
            USER_BY_ID_OR_EMAIL_ENDPOINT.format(id_or_email=id_or_email), expected_status=expected_status
        )
        if response.ok:
            user = User.model_validate(response.json())
            log_event(self.logger, "user", "get_success", user_id=user.id, email=user.email)
            return user
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "user",
            "get_failed",
            level=logging.WARNING,
            id_or_email=id_or_email,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_users(self, params: dict | None = None, expected_status: int = 200) -> UsersListApiResponse:
        log_event(self.logger, "user", "list_attempt", params=params or "default")
        response = self.get(USERS_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            data = response.json()
            if isinstance(data, list):
                if not data:
                    log_event(self.logger, "user", "list_success", count=0)
                    return UsersListResponse(users=[], count=0, page=1, pageSize=0)
                if isinstance(data[0], dict) and "users" in data[0]:
                    data = data[0]
                else:
                    users = [User.model_validate(item) for item in data]
                    log_event(self.logger, "user", "list_success", count=len(users))
                    return UsersListResponse(users=users, count=len(users), page=1, pageSize=len(users))
            users_list = UsersListResponse.model_validate(data)
            log_event(self.logger, "user", "list_success", count=users_list.count)
            return users_list
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "user",
            "list_failed",
            level=logging.ERROR,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def edit_user(self, user_id: str, user_data: dict, expected_status: int = 200) -> UserApiResponse:
        log_event(self.logger, "user", "edit_attempt", user_id=user_id)
        response = self.patch(
            USER_BY_ID_ENDPOINT.format(user_id=user_id), json=user_data, expected_status=expected_status
        )
        if response.ok:
            data = response.json()
            data.setdefault("id", user_id)
            user = User.model_validate(data)
            log_event(self.logger, "user", "edit_success", user_id=user.id, email=user.email)
            return user
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "user",
            "edit_failed",
            level=logging.ERROR,
            user_id=user_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def delete_user(self, user_id: str, expected_status: int = 200) -> UserApiResponse:
        log_event(self.logger, "user", "delete_attempt", user_id=user_id)
        response = self.delete(USER_BY_ID_ENDPOINT.format(user_id=user_id), expected_status=expected_status)
        if response.ok:
            if response.content:
                user = User.model_validate(response.json())
                log_event(self.logger, "user", "delete_success", user_id=user.id, email=user.email)
                return user
            log_event(self.logger, "user", "delete_success", user_id=user_id)
            return None
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "user",
            "delete_failed",
            level=logging.WARNING,
            user_id=user_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error
