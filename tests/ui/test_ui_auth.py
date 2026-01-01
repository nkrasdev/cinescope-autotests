import re

import allure
import pytest
from faker import Faker
from playwright.sync_api import Page, expect

from tests.models.request_models import UserCreate
from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.register_page import RegisterPage
from tests.utils.decorators import allure_test_details


@pytest.mark.ui
@allure.epic("UI тесты")
@allure.feature("Аутентификация")
class TestUIAuth:
    @allure_test_details(
        story="Регистрация нового пользователя",
        title="Успешная регистрация пользователя через UI",
        description="""
        Проверка, что пользователь может успешно зарегистрироваться через пользовательский интерфейс.
        Шаги:
        1. Открыть страницу регистрации.
        2. Сгенерировать валидные данные пользователя (email, пароль, имя).
        3. Заполнить и отправить форму регистрации.
        4. Проверить, что произошел редирект на страницу входа.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_user_registration(self, page: Page, user_credentials_ui: tuple[UserCreate, str]):
        register_page = RegisterPage(page)
        user_payload, password_repeat = user_credentials_ui

        with allure.step("Открыть страницу регистрации и заполнить данные"):
            register_page.open()
            with page.expect_navigation():
                register_page.register_user(user_payload, password_repeat)

        with allure.step("Проверить редирект на страницу логина после регистрации"):
            expect(page).to_have_url(re.compile(r".*/login"))

    @allure_test_details(
        story="Вход существующего пользователя",
        title="Успешный вход пользователя через UI",
        description="""
        Проверка, что ранее зарегистрированный пользователь может успешно войти в систему через UI.
        Шаги:
        1. Создать и зарегистрировать пользователя через API (фикстура).
        2. Открыть страницу входа.
        3. Ввести email и пароль.
        4. Проверить, что пользователь успешно вошел в систему.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_user_login(self, page: Page, registered_user_by_api_ui: UserCreate):
        login_page = LoginPage(page)
        user = registered_user_by_api_ui

        with allure.step("Открыть страницу входа и ввести учетные данные"):
            login_page.open()
            login_page.login(user, user.password)

        with allure.step("Проверить, что пользователь вошел в систему"):
            login_page.check_user_is_logged_in()

    @allure.story("Логин")
    @allure.title("Логин с невалидными кредами")
    def test_login_with_invalid_credentials(self, page: Page, faker_instance: Faker):
        login_page = LoginPage(page)
        login_page.open()
        user = UserCreate(
            email=faker_instance.email(), password=faker_instance.password(), full_name=faker_instance.name()
        )
        login_page.login(user, "wrong_password")

        login_page.check_error_message("Неверная почта или пароль")

    @allure.story("Регистрация")
    @allure.title("Регистрация с несовпадающими паролями")
    def test_registration_with_mismatched_passwords(self, page: Page, user_credentials_ui: tuple[UserCreate, str]):
        user, _ = user_credentials_ui
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register_user(user, "different_password")
        register_page.check_error_message("Пароль не соответствует требованиям")

    @allure.story("Регистрация")
    @allure.title("Регистрация со слабым паролем")
    def test_registration_with_weak_password(self, page: Page, user_credentials_ui: tuple[UserCreate, str]):
        user, _ = user_credentials_ui
        user.password = "123"
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register_user(user, user.password)
        register_page.check_error_message("Пароль должен содержать не менее 8 символов")
