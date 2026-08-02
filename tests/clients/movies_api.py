import logging
from collections.abc import Mapping
from typing import Any

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
from tests.models.response_models import DeletedResource, ErrorResponse, GenreResponse, MoviesPage
from tests.request.custom_requester import CustomRequester
from tests.utils.logging_utils import log_event

type MovieResponse = Movie | ErrorResponse
type DeletedMovieResponse = DeletedResource | ErrorResponse
type MovieWithReviewsResponse = MovieWithReviews | ErrorResponse
type MoviesPageResponse = MoviesPage | ErrorResponse
type ReviewsResponse = list[Review] | Review | ErrorResponse
type GenresResponse = list[GenreResponse] | ErrorResponse
type GenreResponseModel = GenreResponse | ErrorResponse


class MoviesAPI(CustomRequester):
    def create_movie(
        self,
        movie_data: MovieCreate | Mapping[str, Any],
        *,
        expected_status: int = 201,
    ) -> MovieResponse:
        log_name = movie_data.name if isinstance(movie_data, MovieCreate) else "from dict"
        log_event(self.logger, "movie", "create_attempt", name=log_name)

        request_payload = movie_data.model_dump(by_alias=True) if isinstance(movie_data, MovieCreate) else movie_data

        response = self.post(MOVIES_ENDPOINT, json=request_payload, expected_status=expected_status)
        if response.ok:
            movie = Movie.model_validate(response.json())
            log_event(self.logger, "movie", "create_success", movie_id=movie.id, name=movie.name)
            return movie

        return self.parse_and_log_error(
            response,
            domain="movie",
            action="create_failed",
            level=logging.ERROR,
            name=log_name,
        )

    def get_movie_by_id(self, movie_id: int | str, expected_status: int = 200) -> MovieWithReviewsResponse:
        log_event(self.logger, "movie", "get_by_id_attempt", movie_id=movie_id)
        response = self.get(MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            movie = MovieWithReviews.model_validate(response.json())
            log_event(self.logger, "movie", "get_by_id_success", movie_id=movie_id, name=movie.name)
            return movie

        return self.parse_and_log_error(
            response,
            domain="movie",
            action="get_by_id_failed",
            level=logging.ERROR,
            movie_id=movie_id,
        )

    def delete_movie(self, movie_id: int | str, expected_status: int = 200) -> DeletedMovieResponse:
        log_event(self.logger, "movie", "delete_attempt", movie_id=movie_id)
        response = self.delete(MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            deleted_resource = DeletedResource.model_validate(response.json())
            log_event(self.logger, "movie", "delete_success", movie_id=deleted_resource.id)
            return deleted_resource

        return self.parse_and_log_error(
            response,
            domain="movie",
            action="delete_failed",
            level=logging.ERROR,
            movie_id=movie_id,
        )

    def get_movies(
        self,
        params: Mapping[str, Any] | None = None,
        *,
        expected_status: int = 200,
    ) -> MoviesPageResponse:
        log_event(self.logger, "movie", "list_attempt", params=params or "default")
        response = self.get(MOVIES_ENDPOINT, params=params, expected_status=expected_status)
        if response.ok:
            movies_page = MoviesPage.model_validate(response.json())
            log_event(self.logger, "movie", "list_success", count=movies_page.count, page_size=len(movies_page.movies))
            return movies_page

        return self.parse_and_log_error(response, domain="movie", action="list_failed", level=logging.ERROR)

    def edit_movie(
        self,
        movie_id: int | str,
        update_payload: Mapping[str, Any],
        expected_status: int = 200,
    ) -> Movie | ErrorResponse:
        log_event(self.logger, "movie", "edit_attempt", movie_id=movie_id)
        response = self.patch(
            MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id), json=update_payload, expected_status=expected_status
        )
        if response.ok:
            movie = Movie.model_validate(response.json())
            log_event(self.logger, "movie", "edit_success", movie_id=movie.id, name=movie.name)
            return movie

        return self.parse_and_log_error(
            response,
            domain="movie",
            action="edit_failed",
            level=logging.ERROR,
            movie_id=movie_id,
        )

    def get_reviews(self, movie_id: int | str, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "list_attempt", movie_id=movie_id)
        response = self.get(REVIEWS_ENDPOINT.format(movie_id=movie_id), expected_status=expected_status)
        if response.ok:
            response_payload = response.json()
            reviews = [Review.model_validate(item) for item in response_payload]
            log_event(self.logger, "review", "list_success", movie_id=movie_id, count=len(reviews))
            return reviews
        return self.parse_and_log_error(
            response,
            domain="review",
            action="list_failed",
            level=logging.ERROR,
            movie_id=movie_id,
        )

    def create_review(
        self,
        movie_id: int | str,
        review_payload: Mapping[str, Any],
        expected_status: int = 201,
    ) -> ReviewsResponse:
        log_event(self.logger, "review", "create_attempt", movie_id=movie_id)
        response = self.post(
            REVIEWS_ENDPOINT.format(movie_id=movie_id),
            json=review_payload,
            expected_status=expected_status,
        )
        if response.ok:
            response_payload = response.json()
            if isinstance(response_payload, list):
                reviews = [Review.model_validate(item) for item in response_payload]
                log_event(self.logger, "review", "create_success", movie_id=movie_id, count=len(reviews))
                return reviews
            review = Review.model_validate(response_payload)
            log_event(self.logger, "review", "create_success", movie_id=movie_id, user_id=review.user_id)
            return review
        return self.parse_and_log_error(
            response,
            domain="review",
            action="create_failed",
            level=logging.ERROR,
            movie_id=movie_id,
        )

    def edit_review(
        self,
        movie_id: int | str,
        review_payload: Mapping[str, Any],
        expected_status: int = 200,
    ) -> ReviewsResponse:
        log_event(self.logger, "review", "edit_attempt", movie_id=movie_id)
        response = self.put(
            REVIEWS_ENDPOINT.format(movie_id=movie_id),
            json=review_payload,
            expected_status=expected_status,
        )
        if response.ok:
            review = Review.model_validate(response.json())
            log_event(self.logger, "review", "edit_success", movie_id=movie_id, user_id=review.user_id)
            return review
        return self.parse_and_log_error(
            response,
            domain="review",
            action="edit_failed",
            level=logging.ERROR,
            movie_id=movie_id,
        )

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
        return self.parse_and_log_error(
            response,
            domain="review",
            action="delete_failed",
            level=logging.ERROR,
            movie_id=movie_id,
        )

    def hide_review(self, movie_id: int | str, user_id: str, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "hide_attempt", movie_id=movie_id, user_id=user_id)
        response = self.patch(
            REVIEW_HIDE_ENDPOINT.format(movie_id=movie_id, user_id=user_id), expected_status=expected_status
        )
        if response.ok:
            review = Review.model_validate(response.json())
            log_event(self.logger, "review", "hide_success", movie_id=movie_id, user_id=review.user_id)
            return review
        return self.parse_and_log_error(
            response,
            domain="review",
            action="hide_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            user_id=user_id,
        )

    def show_review(self, movie_id: int | str, user_id: str, expected_status: int = 200) -> ReviewsResponse:
        log_event(self.logger, "review", "show_attempt", movie_id=movie_id, user_id=user_id)
        response = self.patch(
            REVIEW_SHOW_ENDPOINT.format(movie_id=movie_id, user_id=user_id), expected_status=expected_status
        )
        if response.ok:
            review = Review.model_validate(response.json())
            log_event(self.logger, "review", "show_success", movie_id=movie_id, user_id=review.user_id)
            return review
        return self.parse_and_log_error(
            response,
            domain="review",
            action="show_failed",
            level=logging.ERROR,
            movie_id=movie_id,
            user_id=user_id,
        )

    def get_genres(self, expected_status: int = 200) -> GenresResponse:
        log_event(self.logger, "genre", "list_attempt")
        response = self.get(GENRES_ENDPOINT, expected_status=expected_status)
        if response.ok:
            genres = [GenreResponse.model_validate(item) for item in response.json()]
            log_event(self.logger, "genre", "list_success", count=len(genres))
            return genres
        return self.parse_and_log_error(response, domain="genre", action="list_failed", level=logging.ERROR)

    def get_genre_by_id(self, genre_id: int | str, expected_status: int = 200) -> GenreResponseModel:
        log_event(self.logger, "genre", "get_by_id_attempt", genre_id=genre_id)
        response = self.get(GENRE_BY_ID_ENDPOINT.format(genre_id=genre_id), expected_status=expected_status)
        if response.ok:
            genre = GenreResponse.model_validate(response.json())
            log_event(self.logger, "genre", "get_by_id_success", genre_id=genre.id, name=genre.name)
            return genre
        return self.parse_and_log_error(
            response,
            domain="genre",
            action="get_by_id_failed",
            level=logging.ERROR,
            genre_id=genre_id,
        )

    def create_genre(
        self,
        genre_payload: Mapping[str, Any],
        expected_status: int = 201,
    ) -> GenreResponseModel:
        log_event(self.logger, "genre", "create_attempt", name=genre_payload.get("name"))
        response = self.post(GENRES_ENDPOINT, json=genre_payload, expected_status=expected_status)
        if response.ok:
            genre = GenreResponse.model_validate(response.json())
            log_event(self.logger, "genre", "create_success", genre_id=genre.id, name=genre.name)
            return genre
        return self.parse_and_log_error(
            response,
            domain="genre",
            action="create_failed",
            level=logging.ERROR,
            name=genre_payload.get("name"),
        )

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
        return self.parse_and_log_error(
            response,
            domain="genre",
            action="delete_failed",
            level=logging.ERROR,
            genre_id=genre_id,
        )
