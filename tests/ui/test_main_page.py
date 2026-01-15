import re

import allure
import pytest
from playwright.sync_api import Page, expect

from tests.constants.timeouts import Timeout
from tests.ui.pages.main_page import MainPage
from tests.utils.decorators import allure_test_details


@pytest.mark.ui
@allure.epic("Фильмы")
@allure.feature("Главная страница")
class TestMainPage:
    @pytest.fixture(scope="function", autouse=True)
    def setup(self, page: Page):
        self.main_page = MainPage(page)
        self.main_page.open()

    @allure_test_details(
        story="Отображение элементов",
        title="Видимость секции 'Последние фильмы'",
        description="Проверка, что на главной странице отображается заголовок секции 'Последние фильмы'.",
        severity=allure.severity_level.NORMAL,
    )
    def test_last_movies_section_is_visible(self):
        with allure.step("Проверить видимость заголовка 'Последние фильмы'"):
            self.main_page.check_last_movies_title_is_visible()

    @allure_test_details(
        story="Отображение элементов",
        title="Отображение карточек фильмов",
        description="""
        Проверка, что на главной странице отображаются карточки фильмов и их основные элементы.
        Шаги:
        1. Получить все карточки фильмов со страницы.
        2. Убедиться, что на странице есть хотя бы одна карточка.
        3. Проверить, что у первой карточки виден заголовок, изображение и кнопка 'Подробнее'.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_movie_cards_are_displayed(self):
        with allure.step("Получить все карточки фильмов и убедиться, что они есть"):
            movie_cards = self.main_page.get_movie_cards()
            assert len(movie_cards) > 0, "На главной странице не найдены карточки фильмов."

        with allure.step("Проверить содержимое первой карточки фильма"):
            first_card = movie_cards[0]
            expect(first_card.locator("h3")).to_be_visible()
            expect(first_card.locator("img")).to_be_visible()
            expect(first_card.get_by_role("link", name="Подробнее")).to_be_visible()

    @allure_test_details(
        story="Навигация",
        title="Кнопка 'Подробнее' перенаправляет на страницу фильма",
        description="Проверка, что клик по кнопке 'Подробнее' на карточке фильма ведет на страницу этого фильма.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_more_details_button_redirects_to_movie_page(self, page: Page):
        with allure.step("Получить первую карточку фильма и кликнуть 'Подробнее'"):
            movie_cards = self.main_page.get_movie_cards()
            assert len(movie_cards) > 0, "На главной странице не найдены карточки фильмов."
            first_card = movie_cards[0]
            self.main_page.click_more_button_on_movie_card(first_card)

        with allure.step("Проверить URL страницы деталей фильма"):
            expect(page).to_have_url(re.compile(r"/movies/\d+"))

    @allure_test_details(
        story="Навигация",
        title="Переход на страницу 'Все фильмы' по клику на ссылку",
        description="Проверка, что клик по ссылке 'Все фильмы' в шапке ведет на страницу со списком всех фильмов.",
        severity=allure.severity_level.NORMAL,
    )
    def test_all_movies_link_redirects_to_movies_page(self, page: Page):
        with allure.step("Кликнуть по ссылке 'Все фильмы'"), page.expect_navigation(url="**/movies"):
            self.main_page.click_all_movies_link()

        with allure.step("Проверить, что страница 'Все фильмы' загрузилась"):
            location_filter = page.locator('[data-qa-id="movies_filter_location_select"]')
            expect(location_filter).to_be_visible(timeout=Timeout.FIVE_SECONDS.value)
