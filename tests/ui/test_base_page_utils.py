import pytest

from tests.ui.pages.base_page import BasePage


def test_extract_movie_id_from_href_returns_int() -> None:
    movie_id = BasePage.extract_movie_id_from_href("/movies/123")

    assert movie_id == 123


@pytest.mark.parametrize("href", ["/movies/", "/movie/123", "/movies/abc", ""])
def test_extract_movie_id_from_href_raises_value_error_for_invalid_href(href: str) -> None:
    with pytest.raises(ValueError):
        BasePage.extract_movie_id_from_href(href)
