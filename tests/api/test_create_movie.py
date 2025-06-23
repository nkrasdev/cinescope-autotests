import pytest

class TestCreateMovie:
    def test_create_movie_success(self, admin_api_manager, movie_payload):
        movie_id = None
        try:
            create_response = admin_api_manager.movies_api.create_movie(
                movie_data=movie_payload,
                expected_status=201
            )
            created_movie = create_response.json()
            movie_id = created_movie.get("id")

            assert movie_id is not None
            for key, value in movie_payload.items():
                assert created_movie[key] == value
            assert created_movie["imageUrl"] is None
        finally:
            if movie_id:
                admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)

    def test_create_movie_unauthorized(self, api_manager, movie_payload):
        response = api_manager.movies_api.create_movie(
            movie_data=movie_payload,
            expected_status=401,
        )
        response_json = response.json()
        assert response_json["message"] == "Unauthorized"
        assert response_json["statusCode"] == 401

    def test_create_movie_conflict_duplicate_name(self, admin_api_manager, movie_payload):
        create_response = admin_api_manager.movies_api.create_movie(
            movie_data=movie_payload,
            expected_status=201
        )
        movie_id = create_response.json()["id"]

        try:
            response = admin_api_manager.movies_api.create_movie(
                movie_data=movie_payload,
                expected_status=409
            )
            response_json = response.json()
            assert response_json.get("error") == "Conflict"
            assert "уже существует" in response_json.get("message", "")
        finally:
            admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)

    def test_create_movie_bad_request_empty_body(self, admin_api_manager):
        response = admin_api_manager.movies_api.create_movie(
            movie_data={},
            expected_status=400
        )
        response_json = response.json()
        assert response_json.get("error") == "Bad Request"
        all_error_messages = " ".join(response_json.get("message", []))
        assert "name" in all_error_messages
        assert "price" in all_error_messages
        assert "location" in all_error_messages

    @pytest.mark.parametrize("field_to_break, invalid_value", [
        ("name", 12345),
        ("price", "сто рублей"),
        ("location", "New York"),
        ("genreId", "первый жанр")
    ])
    def test_create_movie_bad_request_invalid_types(self, admin_api_manager, movie_payload, field_to_break, invalid_value):
        invalid_payload = movie_payload.copy()
        invalid_payload[field_to_break] = invalid_value

        response = admin_api_manager.movies_api.create_movie(
            movie_data=invalid_payload,
            expected_status=400
        )
        response_json = response.json()
        assert response_json.get("error") == "Bad Request"
        assert len(response_json.get("message", [])) > 0

