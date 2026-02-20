import re

from playwright.sync_api import Locator, Page, expect

from tests.constants.timeouts import Timeout
from tests.ui.pages.base_page import BasePage


class MoviesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.location_filter: Locator = page.get_by_role("combobox").nth(0)
        self.genre_filter: Locator = page.get_by_role("combobox").nth(1)
        self.sort_by_created_at: Locator = page.get_by_role("combobox").nth(2)
        self.pagination: Locator = page.locator("nav[role='navigation']")
        self.movie_cards: Locator = page.locator(".rounded-xl.border.bg-card")

    def open(self):
        super().open("/movies")

    def check_filters_are_visible(self):
        expect(self.location_filter).to_be_visible()
        expect(self.genre_filter).to_be_visible()

    def check_sorting_is_visible(self):
        expect(self.sort_by_created_at).to_be_visible()

    def check_pagination_is_visible(self):
        expect(self.pagination).to_be_visible()

    def get_movie_cards(self) -> list[Locator]:
        expect(self.movie_cards.first).to_be_visible(timeout=Timeout.DEFAULT_TIMEOUT.value)
        return self.movie_cards.all()

    def click_movie_card(self, card_index: int = 0):
        self.movie_cards.nth(card_index).get_by_role("link", name="Подробнее").click()

    def get_first_movie_details(self) -> dict:
        first_card = self.movie_cards.first
        expect(first_card).to_be_visible(timeout=Timeout.DEFAULT_TIMEOUT.value)
        title = first_card.locator("h3").inner_text()
        more_button = first_card.get_by_role("link", name="Подробнее")
        href = more_button.get_attribute("href")
        assert href is not None, "Movie card 'more' button has no href attribute"
        match = re.search(r"/movies/(\d+)", href)
        assert match is not None, "Could not extract movie ID from href"
        movie_id = match.group(1)
        return {"id": movie_id, "title": title}
