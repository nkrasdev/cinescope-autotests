import logging
from collections.abc import Mapping
from typing import Any

from tests.constants.endpoints import USER_BY_ID_ENDPOINT, USER_BY_ID_OR_EMAIL_ENDPOINT, USERS_ENDPOINT
from tests.models.response_models import ErrorResponse, UsersPage
from tests.models.user_models import UpdatedUser, User
from tests.request.custom_requester import CustomRequester
from tests.utils.logging_utils import log_event

type UsersPageResponse = UsersPage | ErrorResponse
type UserApiResponse = User | ErrorResponse | None
type UpdatedUserApiResponse = UpdatedUser | ErrorResponse


class UsersAPI(CustomRequester):
    def create_user(self, user_data: Mapping[str, Any], expected_status: int = 201) -> UserApiResponse:
        log_event(self.logger, "user", "create_attempt", email=user_data.get("email"))
        response = self.post(USERS_ENDPOINT, json=user_data, expected_status=expected_status)
        if response.ok:
            user = User.model_validate(response.json())
            log_event(self.logger, "user", "create_success", user_id=user.id, email=user.email)
            return user
        return self.parse_and_log_error(response, domain="user", action="create_failed", level=logging.ERROR)

    def get_user(self, id_or_email: str, expected_status: int = 200) -> UserApiResponse:
        log_event(self.logger, "user", "get_attempt", id_or_email=id_or_email)
        response = self.get(
            USER_BY_ID_OR_EMAIL_ENDPOINT.format(id_or_email=id_or_email), expected_status=expected_status
        )
        if response.ok:
            user = User.model_validate(response.json())
            log_event(self.logger, "user", "get_success", user_id=user.id, email=user.email)
            return user
        return self.parse_and_log_error(
            response,
            domain="user",
            action="get_failed",
            level=logging.WARNING,
            id_or_email=id_or_email,
        )

    def get_users(
        self,
        params: Mapping[str, Any] | None = None,
        expected_status: int = 200,
    ) -> UsersPageResponse:
        log_event(self.logger, "user", "list_attempt", params=params or "default")
        response = self.get(USERS_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            users_page = UsersPage.model_validate(response.json())
            log_event(self.logger, "user", "list_success", count=users_page.count)
            return users_page
        return self.parse_and_log_error(response, domain="user", action="list_failed", level=logging.ERROR)

    def edit_user(
        self,
        user_id: str,
        user_data: Mapping[str, Any],
        expected_status: int = 200,
    ) -> UpdatedUserApiResponse:
        log_event(self.logger, "user", "edit_attempt", user_id=user_id)
        response = self.patch(
            USER_BY_ID_ENDPOINT.format(user_id=user_id), json=user_data, expected_status=expected_status
        )
        if response.ok:
            user = UpdatedUser.model_validate(response.json())
            log_event(self.logger, "user", "edit_success", user_id=user_id, email=user.email)
            return user
        return self.parse_and_log_error(
            response,
            domain="user",
            action="edit_failed",
            level=logging.ERROR,
            user_id=user_id,
        )

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
        return self.parse_and_log_error(
            response,
            domain="user",
            action="delete_failed",
            level=logging.WARNING,
            user_id=user_id,
        )
