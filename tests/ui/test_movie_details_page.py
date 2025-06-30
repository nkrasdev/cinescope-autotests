import allure
import pytest
from playwright.sync_api import Page
from tests.ui.pages.movie_details_page import MovieDetailsPage
from tests.ui.pages.login_page import LoginPage
from tests.models.request_models import UserCreate
from tests.ui.pages.main_page import MainPage
from tests.utils.decorators import allure_test_details

@pytest.mark.ui
@allure.epic("UI тесты")
@allure.feature("Страница деталей фильма")
class TestMovieDetailsPage:

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, page: Page):
        with allure.step("Подготовка: получить данные о первом фильме с главной страницы"):
            main_page = MainPage(page)
            main_page.open()
            self.movie_details = main_page.get_first_movie_details()
            self.movie_details_page = MovieDetailsPage(page)

    @allure_test_details(
        story="Отображение элементов",
        title="Отображение деталей фильма",
        description="Проверка, что на странице деталей фильма корректно отображаются его основные атрибуты (название, описание и т.д.).",
        severity=allure.severity_level.NORMAL
    )
    def test_movie_details_are_visible(self, page: Page):
        with allure.step("Открыть страницу деталей фильма"):
            self.movie_details_page.open(self.movie_details["id"])
        with allure.step("Проверить видимость всех элементов с деталями фильма"):
            self.movie_details_page.check_movie_details_are_visible()

    @allure_test_details(
        story="Отображение элементов",
        title="Отображение секции с отзывами",
        description="Проверка, что на странице деталей фильма отображается секция с отзывами и сообщение об их отсутствии.",
        severity=allure.severity_level.NORMAL
    )
    def test_reviews_section_is_visible(self, page: Page):
        with allure.step("Открыть страницу деталей фильма"):
            self.movie_details_page.open(self.movie_details["id"])
        with allure.step("Проверить видимость секции отзывов и сообщения 'Нет отзывов'"):
            self.movie_details_page.check_reviews_section_is_visible()
            self.movie_details_page.check_no_reviews_message_is_visible()

    @allure_test_details(
        story="Навигация",
        title="Кнопка 'Купить билет' перенаправляет на страницу оплаты",
        description="Проверка, что после клика на кнопку 'Купить билет' залогиненный пользователь попадает на страницу оплаты именно этого фильма.",
        severity=allure.severity_level.CRITICAL
    )
    def test_buy_ticket_button_redirects_to_payment_page(self, page: Page, registered_user_by_api_ui: UserCreate):
        with allure.step("Авторизоваться пользователем"):
            login_page = LoginPage(page)
            login_page.open()
            login_page.login(registered_user_by_api_ui, registered_user_by_api_ui.password)
            login_page.check_user_is_logged_in()

        with allure.step("Открыть страницу фильма и нажать 'Купить билет'"):
            self.movie_details_page.open(self.movie_details["id"])
            self.movie_details_page.click_buy_ticket_button()

        with allure.step("Проверить URL страницы оплаты"):
            page.wait_for_url(f"**/payment?movieId={self.movie_details['id']}") 