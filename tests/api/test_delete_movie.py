import pytest
from tests.utils.data_generator import MovieDataGenerator
from tests.constants import NON_EXISTENT_ID

class TestDeleteMovie:

    def test_delete_movie_success(self, admin_api_manager):
        payload = MovieDataGenerator.generate_valid_movie_payload()
        create_response = admin_api_manager.movies_api.create_movie(payload, expected_status=201)
        movie_id = create_response.json()["id"]

        delete_response = admin_api_manager.movies_api.delete_movie(
            movie_id=movie_id,
            expected_status=200
        )
        assert delete_response.json()["id"] == movie_id

        admin_api_manager.movies_api.get_movie_by_id(
            movie_id=movie_id,
            expected_status=404
        )

    def test_delete_movie_unauthorized(self, admin_api_manager, api_manager):
        movie_id = None
        try:
            payload = MovieDataGenerator.generate_valid_movie_payload()
            create_response = admin_api_manager.movies_api.create_movie(payload, expected_status=201)
            movie_id = create_response.json()["id"]

            response = api_manager.movies_api.delete_movie(
                movie_id=movie_id,
                expected_status=401,
            )
            assert response.json()["message"] == "Unauthorized"
        finally:
            if movie_id:
                admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)

    @pytest.mark.parametrize("non_existent_id", [0, -1, NON_EXISTENT_ID])
    def test_delete_non_existent_movie(self, admin_api_manager, non_existent_id):
        response = admin_api_manager.movies_api.delete_movie(
            movie_id=non_existent_id,
            expected_status=404
        )
        assert "Фильм не найден" in response.json()["message"]

    def test_delete_movie_with_bad_request(self, admin_api_manager):
        admin_api_manager.movies_api.delete_movie(
            movie_id="abc",
            expected_status=404
        )