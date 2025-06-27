import allure
import pytest_check as check
import logging
from tests.models.response_models import LoginResponse
from tests.utils.decorators import allure_test_details
from tests.constants.log_messages import LogMessages

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
                email=user_payload.email,
                password=user_payload.password,
                expected_status=200
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
            check.equal(user_object.email, user_payload.email,
                        f"Email пользователя должен быть {user_payload.email}")
            check.equal(user_object.full_name, user_payload.full_name,
                        f"Имя пользователя должно быть {user_payload.full_name}")
            check.equal(user_object.roles, ["USER"], "Роль пользователя должна быть 'USER'")
            check.is_true(user_object.verified, "Пользователь должен быть верифицирован")
            check.is_false(user_object.banned, "Пользователь не должен быть забанен")
            check.is_not_none(user_object.id, "ID пользователя не должен быть пустым")
            check.is_not_none(user_object.created_at, "Дата создания пользователя не должна быть пустой")
            LOGGER.info("Детальная проверка полей в ответе завершена успешно.") 