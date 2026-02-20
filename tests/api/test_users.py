import logging

import allure
import pytest_check as check

from tests.models.response_models import UsersListResponse
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
        LOGGER.info("Запуск теста: test_admin_create_user")
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
        LOGGER.info("Запуск теста: test_get_user_by_email")
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
        LOGGER.info("Запуск теста: test_get_users_list")
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
        LOGGER.info("Запуск теста: test_user_can_delete_self")
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
        LOGGER.info("Запуск теста: test_admin_edit_user")
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
