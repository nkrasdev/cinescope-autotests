from datetime import datetime
from enum import Enum

from pydantic import Field

from tests.models.base import ApiModel
from tests.models.user_models import UserInReview


class Location(str, Enum):
    MSK = "MSK"
    SPB = "SPB"


class Genre(ApiModel):
    name: str


class Review(ApiModel):
    user_id: str | None = Field(None, alias="userId")
    rating: int | None = None
    text: str | None = None
    hidden: bool | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    user: UserInReview | None = None


class Movie(ApiModel):
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
    rating: float = 0.0


class MovieWithReviews(Movie):
    reviews: list[Review]
