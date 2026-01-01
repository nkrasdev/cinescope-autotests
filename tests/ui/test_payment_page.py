import allure
import pytest
from playwright.sync_api import Page

from tests.constants.endpoints import CARD_NUMBER, CVC, EXP_MONTH, EXP_YEAR, HOLDER_NAME
from tests.models.request_models import UserCreate
from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.main_page import MainPage
from tests.ui.pages.payment_page import PaymentPage
from tests.ui.pages.payment_success_page import PaymentSuccessPage
from tests.utils.decorators import allure_test_details


@pytest.mark.ui
@allure.epic("UI тесты")
@allure.feature("Страница оплаты")
class TestPaymentPage:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, page: Page, registered_user_by_api_ui: UserCreate):
        with allure.step("Подготовка: получить данные о фильме с главной страницы"):
            main_page = MainPage(page)
            main_page.open()
            self.movie = main_page.get_first_movie_details()

        with allure.step("Подготовка: залогиниться пользователем, созданным через API"):
            self.user = registered_user_by_api_ui
            login_page = LoginPage(page)
            login_page.open()
            login_page.login(self.user, self.user.password)
            login_page.check_user_is_logged_in()

        with allure.step("Подготовка: перейти на страницу оплаты для выбранного фильма"):
            self.payment_page = PaymentPage(page)
            self.payment_page.open(self.movie["id"])
        yield

    @allure_test_details(
        story="Отображение элементов",
        title="Видимость названия фильма и цены на странице оплаты",
        description="Проверка, что на странице оплаты корректно отображаются название фильма и его цена.",
        severity=allure.severity_level.NORMAL,
    )
    def test_movie_title_and_price_are_visible(self, page: Page):
        with allure.step("Проверить видимость названия фильма"):
            self.payment_page.check_movie_title_is_visible(self.movie["title"])
        with allure.step("Проверить видимость цены"):
            self.payment_page.check_price_is_visible()

    @allure_test_details(
        story="Валидация формы",
        title="Форма оплаты не отправляется с пустыми полями",
        description="Проверка, что при попытке отправить пустую форму оплаты появляется сообщение об ошибке.",
        severity=allure.severity_level.NORMAL,
    )
    def test_payment_form_is_not_submitted_with_empty_fields(self, page: Page):
        with allure.step("Отправить пустую форму оплаты"):
            self.payment_page.submit_payment()
        with allure.step("Проверить появление сообщения о валидации"):
            self.payment_page.check_validation_error_is_visible("Не может быть пустым")

    @allure_test_details(
        story="Сценарии оплаты",
        title="Успешная оплата",
        description="""
        Проверка полного сценария успешной оплаты фильма.
        Шаги:
        1. Подготовить пользователя и фильм (фикстура).
        2. Заполнить платежную форму валидными тестовыми данными.
        3. Отправить форму.
        4. Проверить, что отображается страница с сообщением об успешной оплате.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_successful_payment(self, page: Page):
        with allure.step("Заполнить и отправить платежную форму"):
            self.payment_page.fill_payment_details(
                card_number=CARD_NUMBER,
                card_holder=HOLDER_NAME,
                month=EXP_MONTH,
                year=EXP_YEAR,
                cvc=CVC,
            )
            self.payment_page.submit_payment()

        with allure.step("Проверить сообщение об успешной оплате"):
            payment_success_page = PaymentSuccessPage(page)
            payment_success_page.check_success_message_is_visible()
