import logging

from tests.clients.api_manager import ApiManager
from tests.models.movie_models import Movie
from tests.models.request_models import MovieCreate
from tests.models.response_models import GenreResponse
from tests.utils.logging_utils import log_event

LOGGER = logging.getLogger(__name__)


class MovieFactory:
    """Create movies and remove all tracked resources during fixture teardown."""

    def __init__(self, api_manager: ApiManager) -> None:
        self._api_manager = api_manager
        self._created_movie_ids: list[int] = []

    def create(self, movie_payload: MovieCreate) -> Movie:
        response = self._api_manager.movies_api.create_movie(movie_payload, expected_status=201)
        if not isinstance(response, Movie):
            raise AssertionError(f"Создание фильма вернуло {type(response).__name__} вместо Movie")
        self._created_movie_ids.append(response.id)
        return response

    def mark_deleted(self, movie_id: int) -> None:
        if movie_id in self._created_movie_ids:
            self._created_movie_ids.remove(movie_id)

    def cleanup(self) -> None:
        for movie_id in reversed(self._created_movie_ids):
            try:
                self._api_manager.movies_api.delete_movie(movie_id, expected_status=200)
            except AssertionError:
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_skip",
                    level=logging.WARNING,
                    fixture="movie_factory",
                    resource="movie",
                    resource_id=movie_id,
                    reason="already_deleted_or_unavailable",
                )
        self._created_movie_ids.clear()


class GenreFactory:
    """Create genres and remove all tracked resources during fixture teardown."""

    def __init__(self, api_manager: ApiManager) -> None:
        self._api_manager = api_manager
        self._created_genre_ids: list[int] = []

    def create(self, name: str) -> GenreResponse:
        response = self._api_manager.movies_api.create_genre({"name": name}, expected_status=201)
        if not isinstance(response, GenreResponse):
            raise AssertionError(f"Создание жанра вернуло {type(response).__name__} вместо GenreResponse")
        self._created_genre_ids.append(response.id)
        return response

    def delete(self, genre_id: int) -> GenreResponse:
        response = self._api_manager.movies_api.delete_genre(genre_id, expected_status=200)
        if not isinstance(response, GenreResponse):
            raise AssertionError(f"Удаление жанра вернуло {type(response).__name__} вместо GenreResponse")
        self.mark_deleted(genre_id)
        return response

    def mark_deleted(self, genre_id: int) -> None:
        if genre_id in self._created_genre_ids:
            self._created_genre_ids.remove(genre_id)

    def cleanup(self) -> None:
        for genre_id in reversed(self._created_genre_ids):
            try:
                self._api_manager.movies_api.delete_genre(genre_id, expected_status=200)
            except AssertionError:
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_skip",
                    level=logging.WARNING,
                    fixture="genre_factory",
                    resource="genre",
                    resource_id=genre_id,
                    reason="already_deleted_or_unavailable",
                )
        self._created_genre_ids.clear()
