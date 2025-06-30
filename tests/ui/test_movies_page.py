import allure
import pytest
import re
from playwright.sync_api import Page, expect
from tests.ui.pages.movies_page import MoviesPage
from tests.utils.decorators import allure_test_details

@pytest.mark.ui
@allure.epic("UI тесты")
@allure.feature("Страница со списком фильмов")
class TestMoviesPage:

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, page: Page):
        self.movies_page = MoviesPage(page)
        self.movies_page.open()

    @allure_test_details(
        story="Отображение элементов",
        title="Отображение списка фильмов и карточек",
        description="Проверка, что на странице со списком фильмов присутствуют карточки фильмов.",
        severity=allure.severity_level.NORMAL
    )
    def test_movie_list_and_cards_are_displayed(self):
        with allure.step("Получить карточки фильмов и проверить их наличие"):
            movie_cards = self.movies_page.get_movie_cards()
            assert len(movie_cards) > 0, "На странице фильмов не найдены карточки."

    @allure_test_details(
        story="Отображение элементов",
        title="Видимость фильтров и сортировки",
        description="Проверка, что на странице со списком фильмов отображаются элементы фильтрации и сортировки.",
        severity=allure.severity_level.NORMAL
    )
    def test_filters_and_sorting_are_visible(self):
        with allure.step("Проверить видимость фильтров"):
            self.movies_page.check_filters_are_visible()
        with allure.step("Проверить видимость сортировки"):
            self.movies_page.check_sorting_is_visible()

    @allure_test_details(
        story="Навигация",
        title="Клик по карточке фильма перенаправляет на страницу фильма",
        description="""
        Проверка, что клик по кнопке 'Подробнее' на карточке фильма перенаправляет на верную страницу деталей.
        Шаги:
        1. Получить ID первого фильма на странице.
        2. Кликнуть на его карточку.
        3. Убедиться, что URL в браузере соответствует ID этого фильма.
        """,
        severity=allure.severity_level.CRITICAL
    )
    def test_movie_card_click_redirects_to_movie_page(self, page: Page):
        with allure.step("Получить детали первого фильма и кликнуть на него"):
            movie_details = self.movies_page.get_first_movie_details()
            movie_id = movie_details["id"]
            self.movies_page.click_movie_card()

        with allure.step("Проверить URL страницы деталей фильма"):
            expect(page).to_have_url(re.compile(f"/movies/{movie_id}"))

    @allure_test_details(
        story="Функциональность страницы",
        title="Работа пагинации",
        description="Проверка работоспособности пагинации на странице со списком фильмов.",
        severity=allure.severity_level.NORMAL
    )
    def test_pagination_is_working(self, page: Page):
        with allure.step("Проверить видимость пагинации"):
            self.movies_page.check_pagination_is_visible()

        with allure.step("Перейти на следующую страницу, если она есть"):
            next_button = page.locator("nav[role='navigation']").get_by_role("link", name="Вперёд")
            if next_button.is_visible():
                expect(next_button).to_be_enabled()
                next_button.click()
                expect(page).to_have_url(re.compile(r"/movies\?page=2")) 