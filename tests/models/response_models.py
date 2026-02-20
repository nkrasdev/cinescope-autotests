from pydantic import BaseModel, ConfigDict, Field

from tests.models.movie_models import Movie
from tests.models.user_models import User, UserSummary


class LoginResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    user: UserSummary


class MoviesList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

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


class GenreResponse(BaseModel):
    id: int
    name: str


class UsersListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    users: list[User]
    count: int
    page: int
    page_size: int = Field(alias="pageSize")
