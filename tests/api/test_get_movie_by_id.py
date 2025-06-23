import pytest

from tests.utils.data_generator import MovieDataGenerator

class TestGetMovieById:

    def test_get_existing_movie_by_id(self, admin_api_manager):
        payload = MovieDataGenerator.generate_valid_movie_payload()
        create_response = admin_api_manager.movies_api.create_movie(payload, expected_status=201)
        movie_created = create_response.json()
        movie_id = movie_created["id"]

        try:
            get_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)
            movie_fetched = get_response.json()

            assert movie_fetched["id"] == movie_id
            assert movie_fetched["name"] == payload["name"]
            assert movie_fetched["description"] == payload["description"]
            assert movie_fetched["price"] == payload["price"]
            assert movie_fetched["location"] == payload["location"]
            assert movie_fetched["genreId"] == payload["genreId"]
            assert movie_fetched["published"] == payload["published"]
            assert movie_fetched["reviews"] == [], "У нового фильма не должно быть отзывов"
        finally:
            admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)

    def test_get_movie_not_found(self, admin_api_manager):
        non_existent_id = 999999
        response = admin_api_manager.movies_api.get_movie_by_id(non_existent_id, expected_status=404)
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
            expected_status=400
        )
