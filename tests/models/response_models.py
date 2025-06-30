from typing import Optional, List, Union
from pydantic import BaseModel, Field
from tests.models.user_models import User
from tests.models.movie_models import Movie

class LoginResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    user: User

class MoviesList(BaseModel):
    movies: List[Movie]
    page: int
    page_size: int = Field(alias="pageSize")
    count: int
    page_count: int = Field(alias="pageCount")

class ErrorResponse(BaseModel):
    statusCode: int
    message: Union[str, List[str]]
    error: Optional[str] = None

class DeletedObject(BaseModel):
    id: int 