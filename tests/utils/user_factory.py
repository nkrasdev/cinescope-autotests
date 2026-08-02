import logging
from dataclasses import dataclass, field
from typing import Any

from faker import Faker

from tests.clients.api_manager import ApiManager
from tests.models.request_models import UserCreate
from tests.models.user_models import User
from tests.utils.data_generator import UserDataGenerator
from tests.utils.logging_utils import log_event

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreatedUser:
    user: User
    credentials: UserCreate = field(repr=False)
    request_payload: dict[str, Any] = field(repr=False)


class AdminUserFactory:
    """Create admin-managed users and clean them up after a test."""

    def __init__(self, api_manager: ApiManager, faker: Faker) -> None:
        self._api_manager = api_manager
        self._faker = faker
        self._created_user_ids: list[str] = []

    def create(
        self,
        *,
        verified: bool = True,
        banned: bool = False,
        roles: list[str] | None = None,
    ) -> CreatedUser:
        credentials, _ = UserDataGenerator.generate_user_payload(self._faker)
        request_payload = credentials.model_dump(by_alias=True)
        request_payload.update({"verified": verified, "banned": banned})
        if roles is not None:
            request_payload["roles"] = roles

        response = self._api_manager.users_api.create_user(request_payload, expected_status=201)
        if not isinstance(response, User):
            raise AssertionError(f"Создание пользователя вернуло {type(response).__name__} вместо User")

        self._created_user_ids.append(response.id)
        return CreatedUser(
            user=response,
            credentials=credentials,
            request_payload=request_payload,
        )

    def mark_deleted(self, user_id: str) -> None:
        """Stop tracking a user that was deleted by the scenario itself."""
        if user_id in self._created_user_ids:
            self._created_user_ids.remove(user_id)

    def cleanup(self) -> None:
        for user_id in reversed(self._created_user_ids):
            try:
                self._api_manager.users_api.delete_user(user_id, expected_status=200)
            except AssertionError:
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_skip",
                    level=logging.WARNING,
                    fixture="admin_user_factory",
                    resource="user",
                    resource_id=user_id,
                    reason="already_deleted_or_unavailable",
                )
        self._created_user_ids.clear()


class RegisteredUserFactory:
    """Register users through the public API and clean them up through the admin API."""

    def __init__(
        self,
        registration_api_manager: ApiManager,
        cleanup_api_manager: ApiManager,
        faker: Faker,
    ) -> None:
        self._registration_api_manager = registration_api_manager
        self._cleanup_api_manager = cleanup_api_manager
        self._faker = faker
        self._created_user_ids: list[str] = []

    def create(self) -> CreatedUser:
        credentials, password_repeat = UserDataGenerator.generate_user_payload(self._faker)
        request_payload = credentials.model_dump(by_alias=True)
        request_payload["passwordRepeat"] = password_repeat

        response = self._registration_api_manager.auth_api.register(request_payload, expected_status=201)
        if not isinstance(response, User):
            raise AssertionError(f"Регистрация вернула {type(response).__name__} вместо User")

        self._created_user_ids.append(response.id)
        return CreatedUser(
            user=response,
            credentials=credentials,
            request_payload=request_payload,
        )

    def mark_deleted(self, user_id: str) -> None:
        """Stop tracking a user that was deleted by the scenario itself."""
        if user_id in self._created_user_ids:
            self._created_user_ids.remove(user_id)

    def cleanup(self) -> None:
        for user_id in reversed(self._created_user_ids):
            try:
                self._cleanup_api_manager.users_api.delete_user(user_id, expected_status=200)
            except AssertionError:
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_skip",
                    level=logging.WARNING,
                    fixture="registered_user_factory",
                    resource="user",
                    resource_id=user_id,
                    reason="already_deleted_or_unavailable",
                )
        self._created_user_ids.clear()
