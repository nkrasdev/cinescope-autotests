import re
from playwright.sync_api import Page, expect, Locator
from tests.ui.pages.base_page import BasePage


class MainPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.last_movies_title: Locator = page.locator("h2", has_text="Последние фильмы")
        self.movie_cards: Locator = page.locator(".rounded-xl.border.bg-card:has(a[data-qa-id='more_button'])")
        self.show_more_button: Locator = page.get_by_role("button", name="Показать еще")
        self.all_movies_link: Locator = page.get_by_role("link", name="Все фильмы")

    def open(self):
        super().open("/")

    def check_last_movies_title_is_visible(self):
        expect(self.last_movies_title).to_be_visible()

    def get_movie_cards(self) -> list[Locator]:
        return self.movie_cards.all()

    def get_first_movie_details(self) -> dict:
        first_card = self.movie_cards.first
        details_link = first_card.locator('[data-qa-id="more_button"]')
        href = details_link.get_attribute("href")
        if not href:
            raise ValueError("Could not find href attribute on movie details link.")
        
        match = re.search(r'/movies/(\d+)', href)
        if not match:
            raise ValueError(f"Could not extract movie ID from href: {href}")
            
        movie_id = int(match.group(1))
        title = first_card.locator("h3").inner_text()
        return {"id": movie_id, "title": title}

    def click_more_button_on_movie_card(self, card: Locator):
        card.locator('[data-qa-id="more_button"]').click()

    def click_show_more_button(self):
        self.show_more_button.click()

    def click_all_movies_link(self):
        self.all_movies_link.click() 