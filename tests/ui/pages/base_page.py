import re
from typing import Any

from playwright.sync_api import Locator, Page, expect

from tests.constants.endpoints import BASE_UI_URL


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = BASE_UI_URL.rstrip("/")

    def build_url(self, path: str = "") -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{normalized_path}"

    def open(self, path: str = "") -> None:
        self.page.goto(self.build_url(path), wait_until="domcontentloaded")

    def is_url(self, path: str, timeout: float | None = None) -> None:
        expected_url = self.build_url(path)
        expect(self.page).to_have_url(expected_url, timeout=timeout)

    @staticmethod
    def extract_movie_id_from_href(href: str) -> int:
        match = re.search(r"/movies/(\d+)", href)
        if not match:
            raise ValueError(f"Could not extract movie ID from href: {href}")
        return int(match.group(1))

    def extract_movie_card_details(self, card: Locator) -> dict[str, Any]:
        details_link = card.get_by_role("link", name="Подробнее")
        href = details_link.get_attribute("href")
        if not href:
            raise ValueError("Could not find href attribute on movie details link.")

        return {
            "id": self.extract_movie_id_from_href(href),
            "title": card.locator("h3").inner_text(),
        }
