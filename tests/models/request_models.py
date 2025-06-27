from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Annotated
from tests.models.movie_models import Location, GenreId

class UserCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    full_name: Annotated[str, Field(min_length=1, alias="fullName")]
    password: Annotated[str, Field(min_length=5)]

class MovieCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str, Field(min_length=1, max_length=500)]
    price: Annotated[int, Field(gt=0)]
    location: Location
    genre_id: GenreId = Field(..., alias="genreId")
    published: bool = True 