from tests.ui.pages.movie_details_page import is_payment_url_for_movie


def test_is_payment_url_for_movie_accepts_extra_query_params():
    url = "https://cinescope.ru/payment?movieId=42&source=details"

    assert is_payment_url_for_movie(url, 42)


def test_is_payment_url_for_movie_rejects_wrong_movie_id():
    url = "https://cinescope.ru/payment?movieId=41"

    assert not is_payment_url_for_movie(url, 42)
