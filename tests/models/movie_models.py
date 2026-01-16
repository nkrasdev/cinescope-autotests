from datetime import datetime
from enum import Enum, IntEnum

from pydantic import BaseModel, Field

from tests.models.user_models import UserInReview


class Location(str, Enum):
    MSK = "MSK"
    SPB = "SPB"


class GenreId(IntEnum):
    ACTION = 1
    COMEDY = 2
    DRAMA = 3
    FANTASY = 4
    THRILLER = 5


class Genre(BaseModel):
    name: str


class Review(BaseModel):
    user_id: str | None = Field(None, alias="userId")
    rating: int | None = None
    text: str | None = None
    hidden: bool | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    user: UserInReview | None = None


class Movie(BaseModel):
    id: int
    name: str
    description: str
    price: int
    image_url: str | None = Field(None, alias="imageUrl")
    location: Location
    published: bool
    genre_id: int = Field(alias="genreId")
    genre: Genre
    created_at: datetime = Field(alias="createdAt")
    rating: float


class MovieWithReviews(Movie):
    reviews: list[Review]
