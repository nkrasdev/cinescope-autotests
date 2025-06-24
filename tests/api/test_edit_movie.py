import pytest
from tests.utils.data_generator import MovieDataGenerator
from tests.constants import NON_EXISTENT_ID

class TestEditMovie:

    def test_edit_movie_name_success(self, admin_api_manager, created_movie):
        movie_id = created_movie["id"]

        new_name = "Обновленное название фильма " + MovieDataGenerator.generate_random_title()
        edit_payload = {"name": new_name}

        edit_response = admin_api_manager.movies_api.edit_movie(
            movie_id=movie_id,
            payload=edit_payload,
            expected_status=200
        )

        edited_movie = edit_response.json()
        assert edited_movie["id"] == movie_id, "ID не должен меняться после редактирования"
        assert edited_movie["name"] == new_name
        assert edited_movie["description"] == created_movie["description"]

        get_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)
        fetched_movie = get_response.json()
        assert fetched_movie["name"] == new_name

    def test_edit_movie_unauthorized(self, api_manager, created_movie):
        movie_id = created_movie["id"]

        edit_payload = {"name": "Новое имя"}
        response = api_manager.movies_api.edit_movie(
            movie_id=movie_id,
            payload=edit_payload,
            expected_status=401,
        )
        assert response.json()["message"] == "Unauthorized"

    def test_edit_non_existent_movie(self, admin_api_manager):
        edit_payload = {"name": "Неважно"}
        response = admin_api_manager.movies_api.edit_movie(
            movie_id=NON_EXISTENT_ID,
            payload=edit_payload,
            expected_status=404
        )
        assert "не найден" in response.json()["message"]

    @pytest.mark.parametrize("invalid_data", [
        {"price": "дорого"},
        {"location": "PARIS"},
        {"genreId": "боевик"},
        {"name": 12345}
    ])
    def test_edit_movie_with_invalid_data(self, admin_api_manager, created_movie, invalid_data):
        movie_id = created_movie["id"]

        admin_api_manager.movies_api.edit_movie(
            movie_id=movie_id,
            payload=invalid_data,
            expected_status=400
        )