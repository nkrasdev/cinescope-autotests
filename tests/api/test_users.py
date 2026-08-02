import allure
import pytest

from tests.models.response_models import ErrorResponse, UsersPage
from tests.models.user_models import UpdatedUser, User
from tests.utils.data_generator import UserDataGenerator
from tests.utils.decorators import allure_test_details

NON_EXISTENT_USER_ID = "00000000-0000-0000-0000-000000000000"


def _assert_error_response(response: object, expected_status: int) -> ErrorResponse:
    assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response).__name__}"
    assert response.status_code == expected_status
    return response


@allure.epic("Пользователи")
@allure.feature("Управление пользователями")
class TestUsers:
    @allure_test_details(
        story="Создание пользователя",
        title="Администратор создаёт пользователя",
        description="Администратор создаёт пользователя и получает его данные в ответе.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_admin_create_user(self, admin_user_factory):
        with allure.step("Создать пользователя от имени администратора"):
            created_user = admin_user_factory.create()

        assert created_user.user.email == created_user.credentials.email

    @allure_test_details(
        story="Получение пользователя",
        title="Администратор получает пользователя по email",
        description="Поиск по email возвращает ранее созданного пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_user_by_email(self, admin_api_manager, admin_user_factory):
        created_user = admin_user_factory.create()

        with allure.step("Получить пользователя по email"):
            fetched_user = admin_api_manager.users_api.get_user(
                created_user.credentials.email,
                expected_status=200,
            )

        assert isinstance(fetched_user, User), f"Ожидался User, получен {type(fetched_user).__name__}"
        assert fetched_user.id == created_user.user.id
        assert fetched_user.email == created_user.credentials.email

    @allure_test_details(
        story="Список пользователей",
        title="Администратор получает страницу пользователей",
        description="GET /user возвращает пагинированный список пользователей.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_users_list(self, admin_api_manager):
        with allure.step("Запросить список пользователей"):
            response = admin_api_manager.users_api.get_users(expected_status=200)

        assert isinstance(response, UsersPage), f"Ожидался UsersPage, получен {type(response).__name__}"
        assert isinstance(response.users, list)
        assert response.count >= len(response.users)

    @allure_test_details(
        story="Удаление пользователя",
        title="Пользователь удаляет собственную учётную запись",
        description="Авторизованный пользователь может удалить только свою учётную запись.",
        severity=allure.severity_level.NORMAL,
    )
    def test_user_can_delete_self(self, api_manager, registered_user_factory):
        registered_user = registered_user_factory.create()

        with allure.step("Авторизовать пользователя"):
            api_manager.auth_api.login(
                email=registered_user.credentials.email,
                password=registered_user.credentials.password,
            )

        with allure.step("Удалить собственную учётную запись"):
            deleted_user = api_manager.users_api.delete_user(registered_user.user.id, expected_status=200)
        registered_user_factory.mark_deleted(registered_user.user.id)
        if deleted_user is not None:
            assert isinstance(deleted_user, User)

    @allure_test_details(
        story="Редактирование пользователя",
        title="Администратор блокирует пользователя",
        description="PATCH /user/{id} обновляет признак блокировки пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_admin_edit_user(self, admin_api_manager, admin_user_factory):
        created_user = admin_user_factory.create()
        update_payload = {"roles": ["USER"], "verified": True, "banned": True}

        with allure.step("Заблокировать пользователя"):
            updated_user = admin_api_manager.users_api.edit_user(
                user_id=created_user.user.id,
                user_data=update_payload,
                expected_status=200,
            )

        assert isinstance(updated_user, UpdatedUser), f"Ожидался UpdatedUser, получен {type(updated_user).__name__}"
        assert updated_user.banned

    @allure_test_details(
        story="Список пользователей",
        title="Фильтрация пользователей по роли",
        description="Параметр roles ограничивает выдачу пользователями с выбранной ролью.",
        severity=allure.severity_level.MINOR,
    )
    def test_get_users_filter_by_role(self, admin_api_manager):
        query_params = {"roles": ["USER"]}
        with allure.step(f"Запросить пользователей с фильтром: {query_params}"):
            response = admin_api_manager.users_api.get_users(params=query_params, expected_status=200)

        assert isinstance(response, UsersPage), f"Ожидался UsersPage, получен {type(response).__name__}"
        for user in response.users:
            assert "USER" in user.roles, f"У пользователя {user.id} отсутствует роль USER"

    @allure_test_details(
        story="Список пользователей",
        title="Пагинация списка пользователей",
        description="Параметры page и pageSize ограничивают размер и номер страницы.",
        severity=allure.severity_level.MINOR,
    )
    def test_get_users_with_pagination(self, admin_api_manager):
        page_size = 5
        query_params = {"page": 1, "pageSize": page_size}
        with allure.step(f"Запросить страницу пользователей: {query_params}"):
            response = admin_api_manager.users_api.get_users(params=query_params, expected_status=200)

        assert isinstance(response, UsersPage), f"Ожидался UsersPage, получен {type(response).__name__}"
        assert len(response.users) <= page_size
        assert response.page == 1
        assert response.page_size == page_size


@allure.epic("Пользователи")
@allure.feature("Управление пользователями")
class TestUserErrors:
    @allure_test_details(
        story="Удаление пользователя",
        title="Пользователь не может удалить чужую учётную запись",
        description="Пользователь с ролью USER получает 403 при удалении другого пользователя.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_user_cannot_delete_other_user(
        self,
        api_manager,
        admin_user_factory,
        registered_user_factory,
    ):
        target_user = admin_user_factory.create()
        actor_user = registered_user_factory.create()

        api_manager.auth_api.login(
            email=actor_user.credentials.email,
            password=actor_user.credentials.password,
        )

        with allure.step("Попытаться удалить другого пользователя"):
            response = api_manager.users_api.delete_user(
                target_user.user.id,
                expected_status=403,
            )
        _assert_error_response(response, 403)

    @allure_test_details(
        story="Удаление пользователя",
        title="Удаление несуществующего пользователя возвращает 404",
        description="DELETE /user/{id} возвращает 404 для неизвестного идентификатора.",
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_non_existent_user(self, admin_api_manager):
        response = admin_api_manager.users_api.delete_user(
            NON_EXISTENT_USER_ID,
            expected_status=404,
        )
        _assert_error_response(response, 404)

    @allure_test_details(
        story="Получение пользователя",
        title="Пользователь не может получить административные данные",
        description="Пользователь с ролью USER получает 403 при запросе данных через административный endpoint.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_user_forbidden(self, api_manager, registered_user_factory):
        registered_user = registered_user_factory.create()
        api_manager.auth_api.login(
            email=registered_user.credentials.email,
            password=registered_user.credentials.password,
        )

        response = api_manager.users_api.get_user(registered_user.user.id, expected_status=403)
        _assert_error_response(response, 403)

    @allure_test_details(
        story="Получение пользователя",
        title="Получение несуществующего пользователя возвращает 404",
        description="GET /user/{id} должен возвращать 404 для неизвестного идентификатора.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.xfail(
        reason="API возвращает 200 с пустым телом вместо 404 для несуществующего пользователя",
        strict=True,
    )
    def test_get_non_existent_user(self, admin_api_manager):
        response = admin_api_manager.users_api.get_user(
            NON_EXISTENT_USER_ID,
            expected_status=404,
        )
        _assert_error_response(response, 404)

    @allure_test_details(
        story="Создание пользователя",
        title="Создание пользователя без авторизации возвращает 401",
        description="Неавторизованный запрос POST /user получает 401.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_user_unauthorized(self, api_manager, faker_instance):
        credentials, _ = UserDataGenerator.generate_user_payload(faker_instance)
        request_payload = credentials.model_dump(by_alias=True)
        request_payload.update({"verified": True, "banned": False})

        response = api_manager.users_api.create_user(
            user_data=request_payload,
            expected_status=401,
        )
        _assert_error_response(response, 401)

    @allure_test_details(
        story="Создание пользователя",
        title="Повторный email при создании пользователя возвращает 409",
        description="Администратор не может создать двух пользователей с одинаковым email.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_user_duplicate_email(self, admin_api_manager, admin_user_factory):
        created_user = admin_user_factory.create()

        response = admin_api_manager.users_api.create_user(
            user_data=created_user.request_payload,
            expected_status=409,
        )
        _assert_error_response(response, 409)

    @allure_test_details(
        story="Редактирование пользователя",
        title="Невалидные роли при редактировании возвращают 400",
        description="Поле roles строкового типа нарушает контракт PATCH /user/{id}.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_user_bad_request(self, admin_api_manager, admin_user_factory):
        created_user = admin_user_factory.create()
        invalid_update = {"roles": "INVALID_ROLE", "verified": True, "banned": False}

        response = admin_api_manager.users_api.edit_user(
            user_id=created_user.user.id,
            user_data=invalid_update,
            expected_status=400,
        )
        _assert_error_response(response, 400)

    @allure_test_details(
        story="Редактирование пользователя",
        title="Редактирование несуществующего пользователя возвращает 404",
        description="PATCH /user/{id} должен возвращать 404 для неизвестного идентификатора.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.xfail(
        reason="API возвращает 400 вместо 404 для несуществующего пользователя при PATCH",
        strict=True,
    )
    def test_edit_non_existent_user(self, admin_api_manager):
        response = admin_api_manager.users_api.edit_user(
            user_id=NON_EXISTENT_USER_ID,
            user_data={"roles": ["USER"], "verified": True, "banned": False},
            expected_status=404,
        )
        _assert_error_response(response, 404)
