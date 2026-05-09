import contextlib
import logging

import allure
import pytest_check as check

from tests.models.response_models import ErrorResponse, UsersListResponse
from tests.models.user_models import User
from tests.utils.data_generator import UserDataGenerator
from tests.utils.decorators import allure_test_details

LOGGER = logging.getLogger(__name__)


@allure.epic("Пользователи")
@allure.feature("Управление пользователями")
class TestUsers:
    @allure_test_details(
        story="Создание пользователя",
        title="Тест создания пользователя администратором",
        description="Проверка, что администратор может создать пользователя через API.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_admin_create_user(self, admin_api_manager, faker_instance):
        user_payload, password = UserDataGenerator.generate_user_payload(faker_instance)
        payload = user_payload.model_dump(by_alias=True)
        payload.update({"password": password, "verified": True, "banned": False})
        user_id = None
        try:
            with allure.step("Отправка запроса на создание пользователя"):
                response = admin_api_manager.users_api.create_user(user_data=payload, expected_status=201)
            is_user = isinstance(response, User)
            check.is_true(is_user, f"Ожидался объект User, но получен {type(response)}")
            if is_user:
                user_id = response.id
                check.equal(response.email, user_payload.email)
        finally:
            if user_id:
                try:
                    admin_api_manager.users_api.delete_user(user_id, expected_status=200)
                except AssertionError:
                    LOGGER.warning(f"Пользователь {user_id} уже удален, пропускаем cleanup")

    @allure_test_details(
        story="Получение пользователя",
        title="Тест получения пользователя по email",
        description="Проверка, что администратор может получить пользователя по email.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_user_by_email(self, admin_api_manager, faker_instance):
        user_payload, password = UserDataGenerator.generate_user_payload(faker_instance)
        payload = user_payload.model_dump(by_alias=True)
        payload.update({"password": password, "verified": True, "banned": False})
        user_id = None
        try:
            with allure.step("Создание пользователя"):
                created_user = admin_api_manager.users_api.create_user(user_data=payload, expected_status=201)
            assert isinstance(created_user, User)
            user_id = created_user.id

            with allure.step("Запрос пользователя по email"):
                fetched_user = admin_api_manager.users_api.get_user(user_payload.email, expected_status=200)
            check.is_true(isinstance(fetched_user, User), f"Ожидался объект User, но получен {type(fetched_user)}")
            if isinstance(fetched_user, User):
                check.equal(fetched_user.id, user_id)
                check.equal(fetched_user.email, user_payload.email)
        finally:
            if user_id:
                admin_api_manager.users_api.delete_user(user_id, expected_status=200)

    @allure_test_details(
        story="Список пользователей",
        title="Тест получения списка пользователей",
        description="Проверка, что администратор может получить список пользователей.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_users_list(self, admin_api_manager):
        with allure.step("Запрос списка пользователей"):
            response = admin_api_manager.users_api.get_users(expected_status=200)
        is_list = isinstance(response, UsersListResponse)
        check.is_true(is_list, f"Ожидался объект UsersListResponse, но получен {type(response)}")
        if is_list:
            check.is_instance(response.users, list)
            check.is_not_none(response.count)

    @allure_test_details(
        story="Удаление пользователя",
        title="Тест удаления пользователя самим собой",
        description="Проверка, что пользователь может удалить свою учетную запись.",
        severity=allure.severity_level.NORMAL,
    )
    def test_user_can_delete_self(self, api_manager, admin_api_manager, faker_instance):
        user_payload, password_repeat = UserDataGenerator.generate_user_payload(faker_instance)
        payload = user_payload.model_dump(by_alias=True)
        payload["passwordRepeat"] = password_repeat
        user_id = None
        try:
            with allure.step("Регистрация нового пользователя"):
                registered_user = api_manager.auth_api.register(user_data=payload, expected_status=201)
            assert isinstance(registered_user, User)
            user_id = registered_user.id

            with allure.step("Логин пользователя"):
                api_manager.auth_api.login(
                    email=user_payload.email, password=user_payload.password, expected_status=200
                )

            with allure.step("Удаление пользователя своим токеном"):
                deleted_user = api_manager.users_api.delete_user(user_id, expected_status=200)
            if deleted_user:
                check.is_true(isinstance(deleted_user, User), f"Ожидался объект User, но получен {type(deleted_user)}")
        finally:
            if user_id:
                try:
                    admin_api_manager.users_api.delete_user(user_id, expected_status=200)
                except AssertionError:
                    LOGGER.warning(f"Пользователь {user_id} уже удален, пропускаем cleanup")

    @allure_test_details(
        story="Редактирование пользователя",
        title="Тест редактирования пользователя администратором",
        description="Проверка, что администратор может изменить данные пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_admin_edit_user(self, admin_api_manager, faker_instance):
        user_payload, password = UserDataGenerator.generate_user_payload(faker_instance)
        payload = user_payload.model_dump(by_alias=True)
        payload.update({"password": password, "verified": True, "banned": False})
        user_id = None
        try:
            with allure.step("Создание пользователя"):
                created_user = admin_api_manager.users_api.create_user(user_data=payload, expected_status=201)
            assert isinstance(created_user, User)
            user_id = created_user.id

            edit_payload = {"roles": ["USER"], "verified": True, "banned": True}
            with allure.step("Редактирование пользователя"):
                edited_user = admin_api_manager.users_api.edit_user(
                    user_id=user_id, user_data=edit_payload, expected_status=200
                )
            check.is_true(isinstance(edited_user, User), f"Ожидался объект User, но получен {type(edited_user)}")
            if isinstance(edited_user, User):
                check.is_true(edited_user.banned)
        finally:
            if user_id:
                admin_api_manager.users_api.delete_user(user_id, expected_status=200)


@allure.epic("Пользователи")
@allure.feature("Управление пользователями")
class TestUsersNegative:
    @allure_test_details(
        story="Удаление пользователя",
        title="Тест ошибки: пользователь не может удалить другого пользователя",
        description="Проверка, что USER получает 403 при попытке удалить другого пользователя.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_user_cannot_delete_other_user(self, api_manager, admin_api_manager, faker_instance):
        user_a_payload, pw_a_repeat = UserDataGenerator.generate_user_payload(faker_instance)
        reg_a = user_a_payload.model_dump(by_alias=True)
        reg_a["passwordRepeat"] = pw_a_repeat

        user_b_payload, pw_b = UserDataGenerator.generate_user_payload(faker_instance)
        create_b = user_b_payload.model_dump(by_alias=True)
        create_b.update({"verified": True, "banned": False})

        user_a_id = None
        user_b_id = None
        try:
            with allure.step("Регистрация пользователя A"):
                resp_a = api_manager.auth_api.register(user_data=reg_a, expected_status=201)
            assert isinstance(resp_a, User)
            user_a_id = resp_a.id
            api_manager.auth_api.login(email=user_a_payload.email, password=user_a_payload.password, expected_status=200)

            with allure.step("Создание пользователя B через admin"):
                resp_b = admin_api_manager.users_api.create_user(user_data=create_b, expected_status=201)
            assert isinstance(resp_b, User)
            user_b_id = resp_b.id

            with allure.step("Попытка пользователя A удалить пользователя B"):
                response = api_manager.users_api.delete_user(user_b_id, expected_status=403)
            check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
            if isinstance(response, ErrorResponse):
                check.equal(response.statusCode, 403)
        finally:
            for uid in [user_a_id, user_b_id]:
                if uid:
                    with contextlib.suppress(AssertionError):
                        admin_api_manager.users_api.delete_user(uid, expected_status=200)

    @allure_test_details(
        story="Удаление пользователя",
        title="Тест ошибки удаления несуществующего пользователя",
        description="Проверка, что API возвращает 404 при удалении несуществующего пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_non_existent_user(self, admin_api_manager):
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        with allure.step(f"Попытка удалить несуществующего пользователя с ID {non_existent_id}"):
            response = admin_api_manager.users_api.delete_user(non_existent_id, expected_status=404)
        check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
        if isinstance(response, ErrorResponse):
            check.equal(response.statusCode, 404)

    @allure_test_details(
        story="Получение пользователя",
        title="Тест ошибки получения пользователя без прав администратора",
        description="Проверка, что обычный пользователь получает 403 при запросе данных другого пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_user_forbidden(self, api_manager, admin_api_manager, faker_instance):
        user_payload, pw_repeat = UserDataGenerator.generate_user_payload(faker_instance)
        reg = user_payload.model_dump(by_alias=True)
        reg["passwordRepeat"] = pw_repeat
        user_id = None
        try:
            resp = api_manager.auth_api.register(user_data=reg, expected_status=201)
            assert isinstance(resp, User)
            user_id = resp.id
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=200)

            with allure.step("Попытка обычного пользователя получить данные по ID"):
                response = api_manager.users_api.get_user(user_id, expected_status=403)
            check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
            if isinstance(response, ErrorResponse):
                check.equal(response.statusCode, 403)
        finally:
            if user_id:
                with contextlib.suppress(AssertionError):
                    admin_api_manager.users_api.delete_user(user_id, expected_status=200)

    @allure_test_details(
        story="Получение пользователя",
        title="Тест ошибки получения несуществующего пользователя",
        description="Проверка, что API возвращает 404 для несуществующего ID.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_non_existent_user(self, admin_api_manager):
        with allure.step("Запрос несуществующего пользователя"):
            response = admin_api_manager.users_api.get_user(
                "00000000-0000-0000-0000-000000000000", expected_status=404
            )
        check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
        if isinstance(response, ErrorResponse):
            check.equal(response.statusCode, 404)

    @allure_test_details(
        story="Создание пользователя",
        title="Тест ошибки создания пользователя без прав администратора",
        description="Проверка, что неаутентифицированный запрос на создание пользователя получает 403.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_user_forbidden(self, api_manager, faker_instance):
        user_payload, _ = UserDataGenerator.generate_user_payload(faker_instance)
        create_data = user_payload.model_dump(by_alias=True)
        create_data.update({"verified": True, "banned": False})

        with allure.step("Создание пользователя без токена администратора"):
            response = api_manager.users_api.create_user(user_data=create_data, expected_status=403)
        check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
        if isinstance(response, ErrorResponse):
            check.equal(response.statusCode, 403)

    @allure_test_details(
        story="Создание пользователя",
        title="Тест ошибки создания пользователя с дублирующимся email",
        description="Проверка, что API возвращает 409 при создании пользователя с уже существующим email.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_user_duplicate_email(self, admin_api_manager, faker_instance):
        user_payload, _ = UserDataGenerator.generate_user_payload(faker_instance)
        create_data = user_payload.model_dump(by_alias=True)
        create_data.update({"verified": True, "banned": False})
        user_id = None
        try:
            resp = admin_api_manager.users_api.create_user(user_data=create_data, expected_status=201)
            assert isinstance(resp, User)
            user_id = resp.id

            with allure.step("Повторное создание пользователя с тем же email"):
                response = admin_api_manager.users_api.create_user(user_data=create_data, expected_status=409)
            check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
            if isinstance(response, ErrorResponse):
                check.equal(response.statusCode, 409)
        finally:
            if user_id:
                with contextlib.suppress(AssertionError):
                    admin_api_manager.users_api.delete_user(user_id, expected_status=200)

    @allure_test_details(
        story="Редактирование пользователя",
        title="Тест ошибки редактирования пользователя с невалидными данными",
        description="Проверка, что API возвращает 400 при передаче невалидных данных в PATCH /user/{id}.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_user_bad_request(self, admin_api_manager, faker_instance):
        user_payload, _ = UserDataGenerator.generate_user_payload(faker_instance)
        create_data = user_payload.model_dump(by_alias=True)
        create_data.update({"verified": True, "banned": False})
        user_id = None
        try:
            resp = admin_api_manager.users_api.create_user(user_data=create_data, expected_status=201)
            assert isinstance(resp, User)
            user_id = resp.id

            with allure.step("Редактирование с невалидными данными (roles как строка вместо массива)"):
                response = admin_api_manager.users_api.edit_user(
                    user_id=user_id,
                    user_data={"roles": "INVALID_ROLE", "verified": True, "banned": False},
                    expected_status=400,
                )
            check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
            if isinstance(response, ErrorResponse):
                check.equal(response.statusCode, 400)
        finally:
            if user_id:
                with contextlib.suppress(AssertionError):
                    admin_api_manager.users_api.delete_user(user_id, expected_status=200)

    @allure_test_details(
        story="Редактирование пользователя",
        title="Тест ошибки редактирования несуществующего пользователя",
        description="Проверка, что API возвращает 404 при попытке редактировать несуществующего пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_non_existent_user(self, admin_api_manager):
        with allure.step("Редактирование несуществующего пользователя"):
            response = admin_api_manager.users_api.edit_user(
                user_id="00000000-0000-0000-0000-000000000000",
                user_data={"roles": ["USER"], "verified": True, "banned": False},
                expected_status=404,
            )
        check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
        if isinstance(response, ErrorResponse):
            check.equal(response.statusCode, 404)

    @allure_test_details(
        story="Список пользователей",
        title="Тест получения списка пользователей с фильтром по ролям",
        description="Проверка, что фильтр roles корректно работает в GET /user.",
        severity=allure.severity_level.MINOR,
    )
    def test_get_users_filter_by_role(self, admin_api_manager):
        params = {"roles": ["USER"]}
        with allure.step(f"Запрос списка пользователей с фильтром: {params}"):
            response = admin_api_manager.users_api.get_users(params=params, expected_status=200)
        check.is_true(
            isinstance(response, UsersListResponse), f"Ожидался UsersListResponse, получен {type(response)}"
        )
        if isinstance(response, UsersListResponse):
            for user in response.users:
                check.is_true("USER" in user.roles, f"Пользователь {user.email} не имеет роли USER")

    @allure_test_details(
        story="Список пользователей",
        title="Тест получения списка пользователей с пагинацией",
        description="Проверка, что параметры page и pageSize корректно работают в GET /user.",
        severity=allure.severity_level.MINOR,
    )
    def test_get_users_with_pagination(self, admin_api_manager):
        params = {"page": 1, "pageSize": 5}
        with allure.step(f"Запрос списка пользователей с пагинацией: {params}"):
            response = admin_api_manager.users_api.get_users(params=params, expected_status=200)
        check.is_true(
            isinstance(response, UsersListResponse), f"Ожидался UsersListResponse, получен {type(response)}"
        )
        if isinstance(response, UsersListResponse):
            check.is_true(len(response.users) <= 5, "Количество пользователей не должно превышать pageSize=5")
