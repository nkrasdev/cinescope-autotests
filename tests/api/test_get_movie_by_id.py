import pytest

from tests.constants import NON_EXISTENT_ID

class TestGetMovieById:

    def test_get_existing_movie_by_id(self, admin_api_manager, created_movie):
        movie_id = created_movie["id"]
        get_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)
        movie_fetched = get_response.json()
        for key, value in created_movie.items():
            if key != "reviews":
                assert movie_fetched[key] == value

        assert movie_fetched["reviews"] == [], "У нового фильма не должно быть отзывов"

    def test_get_movie_not_found(self, admin_api_manager):
        response = admin_api_manager.movies_api.get_movie_by_id(NON_EXISTENT_ID, expected_status=404)
        response_json = response.json()
        assert response.status_code == 404
        assert response_json["statusCode"] == 404
        assert response_json["message"] == "Фильм не найден"

    @pytest.mark.parametrize("invalid_id", [0, -1])
    def test_get_movie_not_found_invalid_id(self, admin_api_manager, invalid_id):
        admin_api_manager.movies_api.get_movie_by_id(
            invalid_id,
            expected_status=404
        )

    def test_get_movie_bad_request(self, admin_api_manager):
        admin_api_manager.movies_api.get_movie_by_id(
            "abc",
            expected_status=500
        )
