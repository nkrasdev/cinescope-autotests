import logging

import requests

from tests.constants.endpoints import (
    GENRE_BY_ID_ENDPOINT,
    GENRES_ENDPOINT,
    MOVIE_BY_ID_ENDPOINT,
    MOVIES_ENDPOINT,
    REVIEW_HIDE_ENDPOINT,
    REVIEW_SHOW_ENDPOINT,
    REVIEWS_ENDPOINT,
)
from tests.models.movie_models import Movie, MovieWithReviews, Review
from tests.models.request_models import MovieCreate
from tests.models.response_models import DeletedObject, ErrorResponse, GenreResponse, MoviesList
from tests.request.custom_requester import CustomRequester
from tests.utils.logging_utils import log_event

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
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_movie(self, movie_data: MovieCreate | dict, *, expected_status: int = 201) -> MovieResponse:
        log_name = movie_data.name if isinstance(movie_data, MovieCreate) else "from dict"
        log_event(self.logger, "movie", "create_attempt", name=log_name)

        data = movie_data.model_dump(by_alias=True) if isinstance(movie_data, MovieCreate) else movie_data

        response = self.post(MOVIES_ENDPOINT, json=data, expected_status=expected_status)
        if response.ok:
            movie = Movie.model_validate(response.json())
            log_event(self.logger, "movie", "create_success", movie_id=movie.id, name=movie.name)
            return movie

        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "movie",
            "create_failed",
            level=logging.ERROR,
            name=log_name,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_movie_by_id(self, movie_id: int | str, expected_status: int = 200) -> MovieWithReviews | ErrorResponse:
        log_event(self.logger, "movie", "get_by_id_attempt", movie_id=movie_id)
        response = self.get(MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            movie = MovieWithReviews.model_validate(response.json())
            log_event(self.logger, "movie", "get_by_id_success", movie_id=movie_id, name=movie.name)
            return movie

        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "movie",
            "get_by_id_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def delete_movie(self, movie_id: int | str, expected_status: int = 200) -> DeletedObject | ErrorResponse:
        log_event(self.logger, "movie", "delete_attempt", movie_id=movie_id)
        response = self.delete(MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            deleted_object = DeletedObject.model_validate(response.json())
            log_event(self.logger, "movie", "delete_success", movie_id=deleted_object.id)
            return deleted_object

        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "movie",
            "delete_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_movies(self, params: dict | None = None, *, expected_status: int = 200) -> MoviesList | ErrorResponse:
        log_event(self.logger, "movie", "list_attempt", params=params or "default")
        response = self.get(MOVIES_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            movies_list = MoviesList.model_validate(response.json())
            log_event(self.logger, "movie", "list_success", count=movies_list.count, page_size=len(movies_list.movies))
            return movies_list

        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "movie",
            "list_failed",
            level=logging.ERROR,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_movies_with_invalid_params(self, params: dict, expected_status: int = 400) -> ErrorResponse:
        log_event(self.logger, "movie", "list_invalid_attempt", params=params)
        response = self.get(MOVIES_ENDPOINT, params=params, expected_status=expected_status)
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "movie",
            "list_invalid_expected_error",
            level=logging.WARNING,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def edit_movie(self, movie_id: int | str, payload: dict, expected_status: int = 200) -> Movie | ErrorResponse:
        log_event(self.logger, "movie", "edit_attempt", movie_id=movie_id)
        response = self.patch(
            MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), json=payload, expected_status=expected_status
        )
        if response.ok:
            movie = Movie.model_validate(response.json())
            log_event(self.logger, "movie", "edit_success", movie_id=movie.id, name=movie.name)
            return movie

        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "movie",
            "edit_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_reviews(self, movie_id: int | str, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "list_attempt", movie_id=movie_id)
        response = self.get(REVIEWS_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            data = response.json()
            reviews = [Review.model_validate(item) for item in data]
            log_event(self.logger, "review", "list_success", movie_id=movie_id, count=len(reviews))
            return reviews
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "review",
            "list_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def create_review(self, movie_id: int | str, payload: dict, expected_status: int = 201) -> ReviewsResponse:
        log_event(self.logger, "review", "create_attempt", movie_id=movie_id)
        response = self.post(REVIEWS_ENDPOINT.format(movie_id=movie_id), json=payload, expected_status=expected_status)
        if response.ok:
            data = response.json()
            if isinstance(data, list):
                reviews = [Review.model_validate(item) for item in data]
                log_event(self.logger, "review", "create_success", movie_id=movie_id, count=len(reviews))
                return reviews
            review = Review.model_validate(data)
            log_event(self.logger, "review", "create_success", movie_id=movie_id, user_id=review.user_id)
            return review
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "review",
            "create_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def edit_review(self, movie_id: int | str, payload: dict, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "edit_attempt", movie_id=movie_id)
        response = self.put(REVIEWS_ENDPOINT.format(movie_id=movie_id), json=payload, expected_status=expected_status)
        if response.ok:
            review = Review.model_validate(response.json())
            log_event(self.logger, "review", "edit_success", movie_id=movie_id, user_id=review.user_id)
            return review
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "review",
            "edit_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def delete_review(self, movie_id: int | str, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "delete_attempt", movie_id=movie_id)
        response = self.delete(REVIEWS_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            if response.content:
                review = Review.model_validate(response.json())
                log_event(self.logger, "review", "delete_success", movie_id=movie_id, user_id=review.user_id)
                return review
            log_event(self.logger, "review", "delete_success", movie_id=movie_id)
            return []
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "review",
            "delete_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def hide_review(self, movie_id: int | str, user_id: str, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "hide_attempt", movie_id=movie_id, user_id=user_id)
        response = self.patch(
            REVIEW_HIDE_ENDPOINT.format(movie_id=movie_id, user_id=user_id), expected_status=expected_status
        )
        if response.ok:
            review = Review.model_validate(response.json())
            log_event(self.logger, "review", "hide_success", movie_id=movie_id, user_id=review.user_id)
            return review
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "review",
            "hide_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            user_id=user_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def show_review(self, movie_id: int | str, user_id: str, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "show_attempt", movie_id=movie_id, user_id=user_id)
        response = self.patch(
            REVIEW_SHOW_ENDPOINT.format(movie_id=movie_id, user_id=user_id), expected_status=expected_status
        )
        if response.ok:
            review = Review.model_validate(response.json())
            log_event(self.logger, "review", "show_success", movie_id=movie_id, user_id=review.user_id)
            return review
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "review",
            "show_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            user_id=user_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_genres(self, expected_status: int = 200) -> GenresResponse:
        log_event(self.logger, "genre", "list_attempt")
        response = self.get(GENRES_ENDPOINT, expected_status=expected_status)
        if response.ok:
            genres = [GenreResponse.model_validate(item) for item in response.json()]
            log_event(self.logger, "genre", "list_success", count=len(genres))
            return genres
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "genre",
            "list_failed",
            level=logging.ERROR,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def get_genre_by_id(self, genre_id: int | str, expected_status: int = 200) -> GenreResponseModel:
        log_event(self.logger, "genre", "get_by_id_attempt", genre_id=genre_id)
        response = self.get(GENRE_BY_ID_ENDPOINT.format(genre_id=genre_id), expected_status=expected_status)
        if response.ok:
            genre = GenreResponse.model_validate(response.json())
            log_event(self.logger, "genre", "get_by_id_success", genre_id=genre.id, name=genre.name)
            return genre
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "genre",
            "get_by_id_failed",
            level=logging.ERROR,
            genre_id=genre_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def create_genre(self, payload: dict, expected_status: int = 201) -> GenreResponseModel:
        log_event(self.logger, "genre", "create_attempt", name=payload.get("name"))
        response = self.post(GENRES_ENDPOINT, json=payload, expected_status=expected_status)
        if response.ok:
            genre = GenreResponse.model_validate(response.json())
            log_event(self.logger, "genre", "create_success", genre_id=genre.id, name=genre.name)
            return genre
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "genre",
            "create_failed",
            level=logging.ERROR,
            name=payload.get("name"),
            status_code=error.statusCode,
            error=error.message,
        )
        return error

    def delete_genre(self, genre_id: int | str, expected_status: int = 200) -> GenreResponseModel:
        log_event(self.logger, "genre", "delete_attempt", genre_id=genre_id)
        response = self.delete(GENRE_BY_ID_ENDPOINT.format(genre_id=genre_id), expected_status=expected_status)
        if response.ok:
            if response.content:
                genre = GenreResponse.model_validate(response.json())
                log_event(self.logger, "genre", "delete_success", genre_id=genre.id, name=genre.name)
                return genre
            log_event(self.logger, "genre", "delete_success", genre_id=genre_id)
            return GenreResponse(id=int(genre_id), name="")
        error = ErrorResponse.model_validate(response.json())
        log_event(
            self.logger,
            "genre",
            "delete_failed",
            level=logging.ERROR,
            genre_id=genre_id,
            status_code=error.statusCode,
            error=error.message,
        )
        return error
