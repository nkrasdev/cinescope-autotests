import logging

import requests

from tests.clients.auth_api import AuthAPI
from tests.constants.endpoints import (
    CREATE_MOVIE_ENDPOINT,
    GENRE_BY_ID_ENDPOINT,
    GENRES_ENDPOINT,
    MOVIE_BY_ID_ENDPOINT,
    MOVIES_ENDPOINT,
    REVIEW_HIDE_ENDPOINT,
    REVIEW_SHOW_ENDPOINT,
    REVIEWS_ENDPOINT,
)
from tests.constants.log_messages import LogMessages
from tests.models.movie_models import Movie, MovieWithReviews, Review
from tests.models.request_models import MovieCreate
from tests.models.response_models import DeletedObject, ErrorResponse, GenreResponse, MoviesList
from tests.request.custom_requester import CustomRequester

type MovieResponse = Movie | ErrorResponse
type DeletedMovieResponse = DeletedObject | ErrorResponse
type MovieWithReviewsResponse = MovieWithReviews | ErrorResponse
type MoviesListResponse = MoviesList | ErrorResponse
type ReviewsResponse = list[Review] | Review | ErrorResponse
type GenresResponse = list[GenreResponse] | ErrorResponse
type GenreResponseModel = GenreResponse | ErrorResponse


class MoviesAPI(CustomRequester):
    def __init__(self, session: requests.Session, base_url: str):
        super().__init__(session, base_url)
        self.auth_handler: AuthAPI | None = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_movie(self, movie_data: MovieCreate | dict, *, expected_status: int = 201) -> MovieResponse:
        log_name = movie_data.name if isinstance(movie_data, MovieCreate) else "from dict"
        self.logger.info(LogMessages.Movies.ATTEMPT_CREATE.format(log_name))

        data = movie_data.model_dump(by_alias=True) if isinstance(movie_data, MovieCreate) else movie_data

        response = self.post(CREATE_MOVIE_ENDPOINT, json=data, expected_status=expected_status)
        if response.ok:
            movie = Movie.model_validate(response.json())
            self.logger.info(LogMessages.Movies.CREATE_SUCCESS.format(movie.name, movie.id))
            return movie

        error = ErrorResponse.model_validate(response.json())
        self.logger.error(f"Ошибка создания фильма '{log_name}': {error.message} (status: {error.statusCode})")
        return error

    def get_movie_by_id(self, movie_id: int | str, expected_status: int = 200) -> MovieWithReviews | ErrorResponse:
        self.logger.info(LogMessages.Movies.ATTEMPT_GET_BY_ID.format(movie_id))
        response = self.get(MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            movie = MovieWithReviews.model_validate(response.json())
            self.logger.info(LogMessages.Movies.GET_BY_ID_SUCCESS.format(movie.name, movie_id))
            return movie

        error = ErrorResponse.model_validate(response.json())
        self.logger.error(f"Ошибка получения фильма по ID {movie_id}: {error.message} (status: {error.statusCode})")
        return error

    def delete_movie(self, movie_id: int | str, expected_status: int = 200) -> DeletedObject | ErrorResponse:
        self.logger.info(LogMessages.Movies.ATTEMPT_DELETE.format(movie_id))
        response = self.delete(MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            deleted_object = DeletedObject.model_validate(response.json())
            self.logger.info(LogMessages.Movies.DELETE_SUCCESS.format(movie_id, movie_id))
            return deleted_object

        error = ErrorResponse.model_validate(response.json())
        self.logger.error(f"Ошибка удаления фильма {movie_id}: {error.message} (status: {error.statusCode})")
        return error

    def get_movies(self, params: dict | None = None, *, expected_status: int = 200) -> MoviesList | ErrorResponse:
        self.logger.info(LogMessages.Movies.ATTEMPT_GET_LIST.format(params or "default"))
        response = self.get(MOVIES_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            movies_list = MoviesList.model_validate(response.json())
            self.logger.info(f"Успешно получено {len(movies_list.movies)} фильмов. Всего найдено: {movies_list.count}")
            return movies_list

        error = ErrorResponse.model_validate(response.json())
        self.logger.error(f"Ошибка получения списка фильмов: {error.message} (status: {error.statusCode})")
        return error

    def get_movies_with_invalid_params(self, params: dict, expected_status: int = 400) -> ErrorResponse:
        self.logger.info(LogMessages.Movies.ATTEMPT_GET_LIST_INVALID.format(params))
        response = self.get(MOVIES_ENDPOINT, params=params, expected_status=expected_status)
        error = ErrorResponse.model_validate(response.json())
        self.logger.warning(f"Ожидаемая ошибка при получении фильмов: {error.message} (status: {error.statusCode})")
        return error

    def edit_movie(self, movie_id: int | str, payload: dict, expected_status: int = 200) -> Movie | ErrorResponse:
        self.logger.info(LogMessages.Movies.ATTEMPT_EDIT.format(movie_id))
        response = self.patch(
            MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), json=payload, expected_status=expected_status
        )
        if response.ok:
            movie = Movie.model_validate(response.json())
            self.logger.info(LogMessages.Movies.EDIT_SUCCESS.format(movie.name, movie.id))
            return movie

        error = ErrorResponse.model_validate(response.json())
        self.logger.error(f"Ошибка редактирования фильма {movie_id}: {error.message} (status: {error.statusCode})")
        return error

    def get_reviews(self, movie_id: int | str, expected_status: int = 200) -> ReviewsResponse:
        self.logger.info(f"Попытка получения отзывов для фильма {movie_id}")
        response = self.get(REVIEWS_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            data = response.json()
            return [Review.model_validate(item) for item in data]
        return ErrorResponse.model_validate(response.json())

    def create_review(self, movie_id: int | str, payload: dict, expected_status: int = 201) -> ReviewsResponse:
        self.logger.info(f"Попытка создания отзыва для фильма {movie_id}")
        response = self.post(REVIEWS_ENDPOINT.format(movie_id=movie_id), json=payload, expected_status=expected_status)
        if response.ok:
            data = response.json()
            if isinstance(data, list):
                return [Review.model_validate(item) for item in data]
            return Review.model_validate(data)
        return ErrorResponse.model_validate(response.json())

    def edit_review(self, movie_id: int | str, payload: dict, expected_status: int = 200) -> ReviewsResponse:
        self.logger.info(f"Попытка редактирования отзыва для фильма {movie_id}")
        response = self.put(REVIEWS_ENDPOINT.format(movie_id=movie_id), json=payload, expected_status=expected_status)
        if response.ok:
            return Review.model_validate(response.json())
        return ErrorResponse.model_validate(response.json())

    def delete_review(self, movie_id: int | str, expected_status: int = 200) -> ReviewsResponse:
        self.logger.info(f"Попытка удаления отзыва для фильма {movie_id}")
        response = self.delete(REVIEWS_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            if response.content:
                return Review.model_validate(response.json())
            return []
        return ErrorResponse.model_validate(response.json())

    def hide_review(self, movie_id: int | str, user_id: str, expected_status: int = 200) -> ReviewsResponse:
        self.logger.info(f"Попытка скрыть отзыв для фильма {movie_id} от пользователя {user_id}")
        response = self.patch(
            REVIEW_HIDE_ENDPOINT.format(movie_id=movie_id, user_id=user_id), expected_status=expected_status
        )
        if response.ok:
            return Review.model_validate(response.json())
        return ErrorResponse.model_validate(response.json())

    def show_review(self, movie_id: int | str, user_id: str, expected_status: int = 200) -> ReviewsResponse:
        self.logger.info(f"Попытка показать отзыв для фильма {movie_id} от пользователя {user_id}")
        response = self.patch(
            REVIEW_SHOW_ENDPOINT.format(movie_id=movie_id, user_id=user_id), expected_status=expected_status
        )
        if response.ok:
            return Review.model_validate(response.json())
        return ErrorResponse.model_validate(response.json())

    def get_genres(self, expected_status: int = 200) -> GenresResponse:
        self.logger.info("Попытка получения списка жанров")
        response = self.get(GENRES_ENDPOINT, expected_status=expected_status)
        if response.ok:
            return [GenreResponse.model_validate(item) for item in response.json()]
        return ErrorResponse.model_validate(response.json())

    def get_genre_by_id(self, genre_id: int | str, expected_status: int = 200) -> GenreResponseModel:
        self.logger.info(f"Попытка получения жанра {genre_id}")
        response = self.get(GENRE_BY_ID_ENDPOINT.format(genre_id=genre_id), expected_status=expected_status)
        if response.ok:
            return GenreResponse.model_validate(response.json())
        return ErrorResponse.model_validate(response.json())

    def create_genre(self, payload: dict, expected_status: int = 201) -> GenreResponseModel:
        self.logger.info(f"Попытка создания жанра {payload.get('name')}")
        response = self.post(GENRES_ENDPOINT, json=payload, expected_status=expected_status)
        if response.ok:
            return GenreResponse.model_validate(response.json())
        return ErrorResponse.model_validate(response.json())

    def delete_genre(self, genre_id: int | str, expected_status: int = 200) -> GenreResponseModel:
        self.logger.info(f"Попытка удаления жанра {genre_id}")
        response = self.delete(GENRE_BY_ID_ENDPOINT.format(genre_id=genre_id), expected_status=expected_status)
        if response.ok:
            if response.content:
                return GenreResponse.model_validate(response.json())
            return GenreResponse(id=int(genre_id), name="")
        return ErrorResponse.model_validate(response.json())
