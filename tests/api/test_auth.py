import logging

import allure
import pytest_check as check

from tests.constants.log_messages import LogMessages
from tests.models.response_models import ErrorResponse, LoginResponse
from tests.models.user_models import User
from tests.utils.data_generator import UserDataGenerator
from tests.utils.decorators import allure_test_details

LOGGER = logging.getLogger(__name__)


@allure.epic("Аутентификация")
@allure.feature("Вход в систему")
class TestAuthentication:
    @allure_test_details(
        story="Вход зарегистрированного пользователя",
        title="Тест успешного входа зарегистрированного пользователя",
        description="""
        Проверка, что новый, только что зарегистрированный пользователь, может успешно войти в систему.
        Шаги:
        1. Создание нового пользователя через фикстуру.
        2. Попытка входа в систему с учетными данными этого пользователя.
        3. Проверка, что API возвращает токен доступа и корректные данные пользователя.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_registered_user_can_login(self, new_registered_user):
        LOGGER.info("Запуск теста: test_registered_user_can_login")
        with allure.step("Получение данных нового зарегистрированного пользователя (через фикстуру)"):
            api_manager, user_payload = new_registered_user
            LOGGER.info(f"Тестовые данные для пользователя '{user_payload.email}' подготовлены фикстурой.")

        with allure.step("Попытка входа в систему с учетными данными нового пользователя"):
            LOGGER.info(LogMessages.Auth.ATTEMPT_LOGIN.format(user_payload.email))
            login_response = api_manager.auth_api.login(
                email=user_payload.email, password=user_payload.password, expected_status=200
            )

        with allure.step("Проверка, что ответ API имеет ожидаемый тип LoginResponse"):
            is_login_resp = isinstance(login_response, LoginResponse)
            check.is_true(is_login_resp, f"Ожидался ответ типа LoginResponse, но получен {type(login_response)}")
            if is_login_resp:
                LOGGER.info(LogMessages.Auth.LOGIN_SUCCESS.format(user_payload.email))

        with allure.step("Проверка успешного ответа и наличия токена доступа"):
            check.is_not_none(login_response.access_token, "Токен доступа не должен быть пустым")

        with allure.step("Проверка данных пользователя в ответе"):
            LOGGER.info("Начало детальной проверки полей в ответе для пользователя " + user_payload.email)
            user_object = login_response.user
            check.equal(user_object.email, user_payload.email, f"Email пользователя должен быть {user_payload.email}")
            check.equal(
                user_object.full_name, user_payload.full_name, f"Имя пользователя должно быть {user_payload.full_name}"
            )
            check.equal(user_object.roles, ["USER"], "Роль пользователя должна быть 'USER'")
            check.is_not_none(user_object.id, "ID пользователя не должен быть пустым")
            LOGGER.info("Детальная проверка полей в ответе завершена успешно.")


@allure.epic("Аутентификация")
@allure.feature("Регистрация")
class TestRegistration:
    @allure_test_details(
        story="Регистрация нового пользователя",
        title="Тест успешной регистрации пользователя",
        description="Проверка, что API регистрирует нового пользователя и возвращает его данные.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_register_user_success(self, api_manager, admin_api_manager, faker_instance):
        LOGGER.info("Запуск теста: test_register_user_success")
        user_payload, password_repeat = UserDataGenerator.generate_user_payload(faker_instance)
        payload = user_payload.model_dump(by_alias=True)
        payload["passwordRepeat"] = password_repeat
        user_id = None
        try:
            with allure.step("Отправка запроса на регистрацию нового пользователя"):
                response = api_manager.auth_api.register(user_data=payload, expected_status=201)
            is_user = isinstance(response, User)
            check.is_true(is_user, f"Ожидался объект User, но получен {type(response)}")
            if is_user:
                user_id = response.id
                check.equal(response.email, user_payload.email)
                check.equal(response.full_name, user_payload.full_name)
        finally:
            if user_id:
                admin_api_manager.users_api.delete_user(user_id, expected_status=200)


@allure.epic("Аутентификация")
@allure.feature("Сессия")
class TestSession:
    @allure_test_details(
        story="Обновление токена",
        title="Тест обновления токенов авторизованного пользователя",
        description="Проверка, что refresh-токен обновляется для авторизованного пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_refresh_tokens(self, admin_api_manager):
        LOGGER.info("Запуск теста: test_refresh_tokens")
        with allure.step("Запрос обновления токенов"):
            response = admin_api_manager.auth_api.refresh_token(expected_status=200)
        check.is_true(isinstance(response, dict), "Ожидался ответ в виде словаря")

    @allure_test_details(
        story="Выход из аккаунта",
        title="Тест logout авторизованного пользователя",
        description="Проверка, что logout возвращает успешный ответ.",
        severity=allure.severity_level.NORMAL,
    )
    def test_logout(self, admin_api_manager):
        LOGGER.info("Запуск теста: test_logout")
        with allure.step("Запрос logout"):
            response = admin_api_manager.auth_api.logout(expected_status=200)
        check.is_true(isinstance(response, dict), "Ожидался ответ в виде словаря")

    @allure_test_details(
        story="Подтверждение email",
        title="Тест подтверждения email с невалидным токеном",
        description="Проверка, что API возвращает ошибку при подтверждении email с невалидным токеном.",
        severity=allure.severity_level.MINOR,
    )
    def test_confirm_email_invalid_token(self, api_manager):
        LOGGER.info("Запуск теста: test_confirm_email_invalid_token")
        with allure.step("Запрос подтверждения email с невалидным токеном"):
            response = api_manager.auth_api.confirm_email(
                token="invalid-token",  # nosec B106
                expected_status=404,
            )
        check.is_true(isinstance(response, ErrorResponse), f"Ожидался ответ ErrorResponse, но получен {type(response)}")
        if isinstance(response, ErrorResponse):
            check.equal(response.statusCode, 404)
