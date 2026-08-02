from pydantic import Field

from tests.models.base import ApiModel
from tests.models.movie_models import Movie
from tests.models.user_models import User, UserSummary


class LoginResponse(ApiModel):
    access_token: str = Field(alias="accessToken")
    user: UserSummary


class MoviesPage(ApiModel):
    movies: list[Movie]
    page: int
    page_size: int = Field(alias="pageSize")
    count: int
    page_count: int = Field(alias="pageCount")


class ErrorResponse(ApiModel):
    status_code: int = Field(alias="statusCode")
    message: str | list[str]
    error: str | None = None

    @property
    def message_text(self) -> str:
        """Return one string for either a single API message or validation errors."""
        return " ".join(self.message) if isinstance(self.message, list) else self.message


class DeletedResource(ApiModel):
    id: int


class GenreResponse(ApiModel):
    id: int
    name: str


class UsersPage(ApiModel):
    users: list[User]
    count: int
    page: int
    page_size: int = Field(alias="pageSize")
    page_count: int = Field(alias="pageCount")
