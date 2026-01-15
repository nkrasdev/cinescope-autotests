from pydantic import BaseModel, Field

from tests.models.movie_models import Movie
from tests.models.user_models import UserSummary


class LoginResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    user: UserSummary


class MoviesList(BaseModel):
    movies: list[Movie]
    page: int
    page_size: int = Field(alias="pageSize")
    count: int
    page_count: int = Field(alias="pageCount")


class ErrorResponse(BaseModel):
    statusCode: int
    message: str | list[str]
    error: str | None = None


class DeletedObject(BaseModel):
    id: int
