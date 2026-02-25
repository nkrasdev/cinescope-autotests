from playwright.sync_api import Locator, Page, expect

from tests.constants.timeouts import Timeout
from tests.ui.pages.base_page import BasePage


class MainPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.last_movies_title: Locator = page.locator("h2", has_text="Последние фильмы")
        self.movie_cards: Locator = page.locator(".rounded-xl.border.bg-card")
        self.show_more_button: Locator = page.get_by_role("link", name="Показать еще")
        self.all_movies_link: Locator = page.get_by_role("link", name="Все фильмы")

    def open(self):
        super().open("/")

    def check_last_movies_title_is_visible(self):
        expect(self.last_movies_title).to_be_visible()

    def get_movie_cards(self) -> list[Locator]:
        expect(self.movie_cards.first).to_be_visible(timeout=Timeout.DEFAULT_TIMEOUT.value)
        return self.movie_cards.all()

    def get_first_movie_details(self) -> dict:
        first_card = self.movie_cards.first
        expect(first_card).to_be_visible(timeout=Timeout.DEFAULT_TIMEOUT.value)
        return self.extract_movie_card_details(first_card)

    def click_more_button_on_movie_card(self, card: Locator):
        card.get_by_role("link", name="Подробнее").click()

    def click_show_more_button(self):
        self.show_more_button.click()

    def click_all_movies_link(self):
        self.all_movies_link.click()
