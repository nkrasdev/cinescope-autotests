from typing import Annotated

from pydantic import EmailStr, Field

from tests.models.base import ApiModel
from tests.models.movie_models import Location


class UserCreate(ApiModel):
    email: EmailStr
    full_name: Annotated[str, Field(min_length=1, alias="fullName")]
    password: Annotated[str, Field(min_length=8)]


class MovieCreate(ApiModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str, Field(min_length=1, max_length=500)]
    price: Annotated[int, Field(gt=0)]
    location: Location
    genre_id: Annotated[int, Field(gt=0, alias="genreId")]
    published: bool = True
