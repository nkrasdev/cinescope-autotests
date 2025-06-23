import pytest

class TestGetMovies:

    def test_get_movies_default(self, api_manager):
        response = api_manager.movies_api.get_movies().json()
        assert isinstance(response["movies"], list)
        assert response["page"] == 1
        assert response["pageSize"] == 10

    def test_get_movies_with_pagination(self, api_manager):
        page_size = 5
        params = {"page": 2, "pageSize": page_size}
        response = api_manager.movies_api.get_movies(params=params).json()

        assert isinstance(response["movies"], list)
        assert len(response["movies"]) <= page_size
        assert response["page"] == 2
        assert response["pageSize"] == page_size

    def test_get_movies_price_filter(self, api_manager):
        params = {"minPrice": 100, "maxPrice": 300}
        movies = api_manager.movies_api.get_movies(params=params).json()["movies"]
        for movie in movies:
            assert 100 <= movie["price"] <= 300

    def test_get_movies_location_filter(self, admin_api_manager, movie_payload):
        movie_id = None
        try:
            movie_payload["location"] = "MSK"
            create_response = admin_api_manager.movies_api.create_movie(movie_payload)
            movie_id = create_response.json()["id"]

            params = {"locations": ["MSK"]}
            movies = admin_api_manager.movies_api.get_movies(params=params).json()["movies"]

            assert len(movies) > 0, "Должен найтись хотя бы один фильм"
            for movie in movies:
                assert movie["location"] == "MSK"
        finally:
            if movie_id:
                admin_api_manager.movies_api.delete_movie(movie_id)

    def test_get_movies_genre_filter(self, api_manager):
        params = {"genreId": 1}
        movies = api_manager.movies_api.get_movies(params=params).json()["movies"]
        for movie in movies:
            assert movie["genreId"] == 1

    def test_get_movies_sort_created_at(self, api_manager):
        params = {"createdAt": "desc"}
        movies = api_manager.movies_api.get_movies(params=params).json()["movies"]
        dates = [movie["createdAt"] for movie in movies]
        assert dates == sorted(dates, reverse=True)

    def test_get_movies_published_default(self, api_manager):
        movies = api_manager.movies_api.get_movies().json()["movies"]
        for movie in movies:
            assert movie["published"] is True

    def test_get_movies_unpublished(self, api_manager):
        params = {"published": False}
        movies = api_manager.movies_api.get_movies(params=params).json()["movies"]
        for movie in movies:
            assert movie["published"] is False

    @pytest.mark.parametrize("params", [
        {"pageSize": "abc"},
        {"pageSize": 0},
        {"pageSize": 21}
    ])
    def test_invalid_page_size(self, api_manager, params):
        response = api_manager.movies_api.get_movies_with_invalid_params(
            params=params,
            expected_status=400
        )
        assert response.status_code == 400
        assert "pageSize" in str(response.json())

    def test_invalid_location(self, api_manager):
        params = {"locations": ["NY"]}
        response = api_manager.movies_api.get_movies_with_invalid_params(
            params=params,
            expected_status=400
        )
        assert response.status_code == 400
        assert "locations" in str(response.json())

    def test_invalid_created_at_enum(self, api_manager):
        params = {"createdAt": "random"}
        response = api_manager.movies_api.get_movies_with_invalid_params(
            params=params,
            expected_status=400
        )
        assert response.status_code == 400
        response_json = response.json()
        assert "message" in response_json
        assert response_json["message"] == "Некорректные данные"

    def test_invalid_genre_id(self, api_manager):
        params = {"genreId": 0}
        response = api_manager.movies_api.get_movies_with_invalid_params(
            params=params,
            expected_status=400
        )
        assert response.status_code == 400
        assert "genreId" in str(response.json())
