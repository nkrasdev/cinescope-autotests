from playwright.sync_api import Locator, Page, expect

from tests.ui.pages.base_page import BasePage


class MovieDetailsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.movie_title: Locator = page.locator("section h2")
        self.movie_description: Locator = page.locator("section h2 + p")
        self.movie_genre: Locator = page.locator("p", has_text="Жанр:")
        self.movie_rating: Locator = page.locator("h3", has_text="Рейтинг:")
        self.movie_image: Locator = page.locator("section img")
        self.buy_ticket_button: Locator = page.locator("[data-qa-id='movie_buy_ticket_button']")
        self.reviews_title: Locator = page.locator("h2", has_text="Отзывы:")
        self.no_reviews_message: Locator = page.get_by_text("Отзывов нет. Оставьте отзыв первым!")

    def open(self, movie_id: int):
        super().open(f"/movies/{movie_id}")

    def check_movie_details_are_visible(self):
        expect(self.movie_title).to_be_visible()
        expect(self.movie_description).to_be_visible()
        expect(self.movie_genre).to_be_visible()
        expect(self.movie_rating).to_be_visible()
        expect(self.movie_image).to_be_visible()
        expect(self.buy_ticket_button).to_be_visible()

    def check_reviews_section_is_visible(self):
        expect(self.reviews_title).to_be_visible()

    def check_no_reviews_message_is_visible(self):
        expect(self.no_reviews_message).to_be_visible()

    def click_buy_ticket_button(self):
        self.buy_ticket_button.click()
