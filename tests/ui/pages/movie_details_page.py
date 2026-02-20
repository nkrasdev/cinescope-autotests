import re
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Locator, Page, expect

from tests.constants.timeouts import Timeout
from tests.ui.pages.base_page import BasePage


def is_payment_url_for_movie(url: str, movie_id: int) -> bool:
    parsed_url = urlparse(url)
    path_matches = parsed_url.path.rstrip("/").endswith("/payment")
    query_movie_ids = parse_qs(parsed_url.query).get("movieId", [])
    return path_matches and str(movie_id) in query_movie_ids


class MovieDetailsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.movie_title: Locator = page.locator("main h2").first
        self.movie_description: Locator = page.locator("main h2 + p").first
        self.movie_genre: Locator = page.locator("p", has_text="Жанр:")
        self.movie_rating: Locator = page.locator("h3", has_text="Рейтинг:")
        self.movie_image: Locator = page.locator("main img").first
        self.buy_ticket_button: Locator = page.get_by_role("link", name=re.compile(r"Купить билет"))
        self.reviews_title: Locator = page.locator("h2", has_text="Отзывы:")
        self.no_reviews_message: Locator = page.get_by_text("Отзывов нет. Оставьте отзыв первым!")

    def open(self, movie_id: int):
        super().open(f"/movies/{movie_id}")

    def check_movie_details_are_visible(self):
        expect(self.movie_title).to_be_visible()
        expect(self.movie_description).to_be_visible()
        expect(self.movie_genre).to_be_visible()
        expect(self.movie_rating).to_be_visible()
        expect(self.buy_ticket_button).to_be_visible()

    def check_reviews_section_is_visible(self):
        expect(self.reviews_title).to_be_visible()

    def check_no_reviews_message_is_visible(self):
        expect(self.no_reviews_message).to_be_visible()

    def click_buy_ticket_button(self, movie_id: int):
        expect(self.buy_ticket_button).to_be_visible(timeout=Timeout.TEN_SECONDS.value)
        expect(self.buy_ticket_button).to_have_attribute("href", re.compile(rf".*movieId={movie_id}"))
        self.buy_ticket_button.click()
        self.page.wait_for_url(lambda url: is_payment_url_for_movie(url, movie_id), timeout=Timeout.TEN_SECONDS.value)
