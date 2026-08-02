from datetime import UTC, datetime
from unittest.mock import Mock, patch

from tests.clients.users_api import UsersAPI
from tests.models.response_models import UsersPage
from tests.models.user_models import UpdatedUser


def _user_payload() -> dict[str, object]:
    return {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "user@example.com",
        "fullName": "Тестовый Пользователь",
        "roles": ["USER"],
        "verified": True,
        "banned": False,
        "createdAt": datetime.now(UTC).isoformat(),
    }


def _users_api() -> UsersAPI:
    session = Mock()
    session.headers = {}
    return UsersAPI(session=session, base_url="https://auth.example.test")


def test_get_users_parses_documented_page_envelope() -> None:
    users_api = _users_api()
    response = Mock(ok=True)
    response.json.return_value = {
        "users": [_user_payload()],
        "count": 1,
        "page": 1,
        "pageSize": 10,
        "pageCount": 1,
    }
    with patch.object(users_api, "get", return_value=response):
        users_page = users_api.get_users()

    assert isinstance(users_page, UsersPage)
    assert users_page.count == 1
    assert users_page.users[0].email == "user@example.com"


def test_edit_user_parses_response_without_inventing_missing_id() -> None:
    users_api = _users_api()
    response = Mock(ok=True)
    user_without_id = _user_payload()
    user_without_id.pop("id")
    response.json.return_value = user_without_id
    with patch.object(users_api, "patch", return_value=response):
        updated_user = users_api.edit_user(
            user_id="00000000-0000-0000-0000-000000000001",
            user_data={"banned": True},
        )

    assert isinstance(updated_user, UpdatedUser)
    assert not hasattr(updated_user, "id")
