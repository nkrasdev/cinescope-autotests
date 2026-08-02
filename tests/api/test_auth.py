from uuid import uuid4

import allure
import pytest

from tests.models.response_models import ErrorResponse, LoginResponse
from tests.utils.decorators import allure_test_details


@allure.epic("Аутентификация")
@allure.feature("Вход в систему")
class TestAuthentication:
    @allure_test_details(
        story="Вход зарегистрированного пользователя",
        title="Проверка успешного входа зарегистрированного пользователя",
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
        with allure.step("Получение данных нового зарегистрированного пользователя (через фикстуру)"):
            api_manager, user_payload = new_registered_user

        with allure.step("Попытка входа в систему с учетными данными нового пользователя"):
            login_response = api_manager.auth_api.login(
                email=user_payload.email, password=user_payload.password, expected_status=201
            )

        with allure.step("Проверка, что ответ API имеет ожидаемый тип LoginResponse"):
            assert isinstance(login_response, LoginResponse), (
                f"Ожидался LoginResponse, получен {type(login_response).__name__}"
            )

        with allure.step("Проверка успешного ответа и наличия токена доступа"):
            assert login_response.access_token is not None, "Токен доступа не должен быть пустым"

        with allure.step("Проверка данных пользователя в ответе"):
            user_object = login_response.user
            assert user_object.email == user_payload.email, f"Email пользователя должен быть {user_payload.email}"
            assert user_object.full_name == user_payload.full_name, (
                f"Имя пользователя должно быть {user_payload.full_name}"
            )
            assert user_object.roles == ["USER"], "Роль пользователя должна быть 'USER'"
            assert user_object.id is not None, "ID пользователя не должен быть пустым"


@allure.epic("Аутентификация")
@allure.feature("Вход в систему")
class TestLoginErrors:
    @allure_test_details(
        story="Ошибки входа",
        title="Проверка ошибки входа с неверным паролем",
        description="Проверка, что API возвращает 401 при входе с неверным паролем.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_login_wrong_password(self, api_manager, admin_user_factory):
        created_user = admin_user_factory.create()

        with allure.step("Попытка входа с неверным паролем"):
            wrong_password = f"Wrong-{uuid4().hex}"
            response = api_manager.auth_api.login(
                email=created_user.credentials.email,
                password=wrong_password,
                expected_status=401,
            )
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401

    @allure_test_details(
        story="Ошибки входа",
        title="Проверка ошибки входа с неизвестным email",
        description="Проверка, что API возвращает 401 при входе с email, которого нет в системе.",
        severity=allure.severity_level.NORMAL,
    )
    def test_login_with_unknown_email(self, api_manager):
        with allure.step("Попытка входа с несуществующим email"):
            synthetic_password = f"Synthetic-{uuid4().hex}"
            response = api_manager.auth_api.login(
                email="nonexistent-autotest-404@example.com",
                password=synthetic_password,
                expected_status=401,
            )
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401

    @allure_test_details(
        story="Ошибки входа",
        title="Проверка ошибки входа неподтверждённого пользователя",
        description="Проверка, что API возвращает 403 при входе пользователя с verified=false.",
        severity=allure.severity_level.CRITICAL,
    )
    @pytest.mark.xfail(reason="API позволяет вход с verified=False — флаг не проверяется при логине", strict=True)
    def test_login_unconfirmed_user(self, api_manager, admin_user_factory):
        with allure.step("Создание неподтверждённого пользователя через admin API"):
            created_user = admin_user_factory.create(verified=False)

        with allure.step("Попытка входа неподтверждённого пользователя"):
            response = api_manager.auth_api.login(
                email=created_user.credentials.email,
                password=created_user.credentials.password,
                expected_status=403,
            )
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 403


@allure.epic("Аутентификация")
@allure.feature("Регистрация")
class TestRegistration:
    @allure_test_details(
        story="Регистрация нового пользователя",
        title="Проверка успешной регистрации пользователя",
        description="Проверка, что API регистрирует нового пользователя и возвращает его данные.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_register_user_success(self, registered_user_factory):
        with allure.step("Отправка запроса на регистрацию нового пользователя"):
            registered_user = registered_user_factory.create()

        assert registered_user.user.email == registered_user.credentials.email
        assert registered_user.user.full_name == registered_user.credentials.full_name

    @allure_test_details(
        story="Ошибки регистрации",
        title="Проверка ошибки регистрации с пустым телом",
        description="Проверка, что API возвращает 400 при регистрации с пустым телом запроса.",
        severity=allure.severity_level.NORMAL,
    )
    def test_register_bad_request_empty_body(self, api_manager):
        with allure.step("Отправка запроса регистрации с пустым телом"):
            response = api_manager.auth_api.register(user_data={}, expected_status=400)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 400

    @allure_test_details(
        story="Ошибки регистрации",
        title="Проверка ошибки регистрации с уже существующим email",
        description="Проверка, что API возвращает 409 при регистрации с email, который уже используется.",
        severity=allure.severity_level.NORMAL,
    )
    def test_register_duplicate_email(self, new_registered_user):
        api_manager, user_payload = new_registered_user
        registration_payload = user_payload.model_dump(by_alias=True)
        registration_payload["passwordRepeat"] = user_payload.password

        with allure.step("Повторная регистрация с тем же email"):
            response = api_manager.auth_api.register(user_data=registration_payload, expected_status=409)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 409


@allure.epic("Аутентификация")
@allure.feature("Сессия")
class TestSession:
    @allure_test_details(
        story="Обновление токена",
        title="Проверка обновления токенов авторизованного пользователя",
        description="Проверка, что refresh-токен обновляется для авторизованного пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_refresh_tokens(self, new_registered_user):
        api_manager, user_payload = new_registered_user
        api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        with allure.step("Запрос обновления токенов"):
            response = api_manager.auth_api.refresh_token(expected_status=201)
        assert isinstance(response, dict), "Ожидался ответ в виде словаря"

    @allure_test_details(
        story="Выход из аккаунта",
        title="Проверка выхода авторизованного пользователя",
        description="Проверка, что logout возвращает успешный ответ.",
        severity=allure.severity_level.NORMAL,
    )
    def test_logout(self, new_registered_user):
        api_manager, user_payload = new_registered_user
        api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        with allure.step("Запрос logout"):
            response = api_manager.auth_api.logout(expected_status=200)
        assert isinstance(response, dict), "Ожидался ответ в виде словаря"

    @allure_test_details(
        story="Подтверждение email",
        title="Проверка подтверждения email с невалидным токеном",
        description="Проверка, что API возвращает ошибку при подтверждении email с невалидным токеном.",
        severity=allure.severity_level.MINOR,
    )
    def test_confirm_email_invalid_token(self, api_manager):
        with allure.step("Запрос подтверждения email с невалидным токеном"):
            response = api_manager.auth_api.confirm_email(
                token="invalid-token",  # nosec B106
                expected_status=404,
            )
        assert isinstance(response, ErrorResponse), f"Ожидался ответ ErrorResponse, но получен {type(response)}"
        assert response.status_code == 404

    @allure_test_details(
        story="Обновление токена",
        title="Проверка ошибки обновления токена без авторизации",
        description="Проверка, что refresh-endpoint возвращает 401 без токена авторизации.",
        severity=allure.severity_level.NORMAL,
    )
    def test_refresh_tokens_unauthorized(self, api_manager):
        with allure.step("Запрос обновления токенов без авторизации"):
            response = api_manager.auth_api.refresh_token(expected_status=401)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401
