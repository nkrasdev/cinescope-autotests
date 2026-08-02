from datetime import UTC, datetime
from typing import cast
from unittest.mock import Mock

from faker import Faker

from tests.clients.api_manager import ApiManager
from tests.models.user_models import User
from tests.utils.user_factory import AdminUserFactory, RegisteredUserFactory


def test_admin_user_factory_creates_and_cleans_up_user() -> None:
    manager_mock = Mock()
    created_user = User.model_validate(
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "created@example.com",
            "full_name": "Тестовый Пользователь",
            "roles": ["USER"],
            "verified": True,
            "banned": False,
            "created_at": datetime.now(UTC),
        }
    )
    manager_mock.users_api.create_user.return_value = created_user
    factory = AdminUserFactory(cast(ApiManager, manager_mock), Faker("ru_RU"))

    factory_result = factory.create(verified=True, banned=False, roles=["USER"])
    factory.cleanup()

    assert factory_result.user is created_user
    create_payload = manager_mock.users_api.create_user.call_args.args[0]
    assert create_payload["verified"] is True
    assert create_payload["banned"] is False
    assert create_payload["roles"] == ["USER"]
    manager_mock.users_api.delete_user.assert_called_once_with(created_user.id, expected_status=200)


def test_registered_user_factory_registers_and_cleans_up_user() -> None:
    registration_manager = Mock()
    cleanup_manager = Mock()
    registered_user = User.model_validate(
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "email": "registered@example.com",
            "full_name": "Зарегистрированный Пользователь",
            "roles": ["USER"],
            "verified": True,
            "banned": False,
            "created_at": datetime.now(UTC),
        }
    )
    registration_manager.auth_api.register.return_value = registered_user
    factory = RegisteredUserFactory(
        cast(ApiManager, registration_manager),
        cast(ApiManager, cleanup_manager),
        Faker("ru_RU"),
    )

    factory_result = factory.create()
    factory.cleanup()

    assert factory_result.user is registered_user
    registration_payload = registration_manager.auth_api.register.call_args.args[0]
    assert registration_payload["passwordRepeat"] == factory_result.credentials.password
    cleanup_manager.users_api.delete_user.assert_called_once_with(registered_user.id, expected_status=200)
