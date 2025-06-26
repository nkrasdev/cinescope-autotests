import allure

@allure.epic("Аутентификация")
@allure.feature("Вход в систему")
class TestAuthentication:

    @allure.story("Вход зарегистрированного пользователя")
    @allure.title("Тест успешного входа зарегистрированного пользователя")
    @allure.description("""
    Проверка, что новый, только что зарегистрированный пользователь, может успешно войти в систему.
    Шаги:
    1. Создание нового пользователя через фикстуру.
    2. Попытка входа в систему с учетными данными этого пользователя.
    3. Проверка, что API возвращает токен доступа и корректные данные пользователя.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_registered_user_can_login(self, new_registered_user):
        with allure.step("Получение данных нового зарегистрированного пользователя (через фикстуру)"):
            api_manager, user_credentials = new_registered_user

        with allure.step("Попытка входа в систему с учетными данными нового пользователя"):
            login_response = api_manager.auth_api.login(
                email=user_credentials["email"],
                password=user_credentials["password"],
                expected_status=200
            )

        with allure.step("Проверка успешного ответа и наличия токена доступа"):
            assert login_response.access_token is not None, "Токен доступа не должен быть пустым"

        with allure.step("Проверка данных пользователя в ответе"):
            user_object = login_response.user
            assert user_object.email == user_credentials["email"], f"Email пользователя должен быть {user_credentials['email']}"
            assert user_object.full_name == user_credentials["fullName"], f"Имя пользователя должно быть {user_credentials['fullName']}"
            assert user_object.roles == ["USER"], "Роль пользователя должна быть 'USER'"
            assert user_object.verified is True, "Пользователь должен быть верифицирован"
            assert user_object.banned is False, "Пользователь не должен быть забанен"
            assert user_object.id is not None, "ID пользователя не должен быть пустым"
            assert user_object.created_at is not None, "Дата создания пользователя не должна быть пустой" 