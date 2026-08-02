from datetime import UTC, datetime
from typing import cast
from unittest.mock import Mock

from tests.clients.api_manager import ApiManager
from tests.models.movie_models import Genre, Location, Movie
from tests.models.request_models import MovieCreate
from tests.models.response_models import GenreResponse
from tests.utils.catalog_factory import GenreFactory, MovieFactory


def _movie() -> Movie:
    return Movie.model_validate(
        {
            "id": 42,
            "name": "Фильм",
            "description": "Описание",
            "price": 500,
            "location": Location.MSK,
            "published": True,
            "genre_id": 1,
            "genre": Genre(name="Боевик"),
            "created_at": datetime.now(UTC),
        }
    )


def _movie_payload() -> MovieCreate:
    return MovieCreate.model_validate(
        {
            "name": "Фильм",
            "description": "Описание",
            "price": 500,
            "location": Location.MSK,
            "genre_id": 1,
        }
    )


def test_movie_factory_cleans_up_created_movie() -> None:
    manager = Mock()
    manager.movies_api.create_movie.return_value = _movie()
    factory = MovieFactory(cast(ApiManager, manager))

    created_movie = factory.create(_movie_payload())
    factory.cleanup()

    assert created_movie.id == 42
    manager.movies_api.delete_movie.assert_called_once_with(42, expected_status=200)


def test_genre_factory_does_not_delete_resource_twice() -> None:
    manager = Mock()
    genre = GenreResponse(id=7, name="Новый жанр")
    manager.movies_api.create_genre.return_value = genre
    manager.movies_api.delete_genre.return_value = genre
    factory = GenreFactory(cast(ApiManager, manager))

    created_genre = factory.create(genre.name)
    deleted_genre = factory.delete(created_genre.id)
    factory.cleanup()

    assert deleted_genre == genre
    manager.movies_api.delete_genre.assert_called_once_with(genre.id, expected_status=200)
