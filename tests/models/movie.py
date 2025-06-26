from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from tests.models.enums import Location
from tests.models.genre import Genre
from tests.models.review import Review


class Movie(BaseModel):
    id: int
    name: str
    description: str
    price: int
    image_url: Optional[str] = Field(alias="imageUrl")
    location: Location
    published: bool
    genre_id: int = Field(alias="genreId")
    genre: Genre
    created_at: datetime = Field(alias="createdAt")
    rating: float


class MovieWithReviews(Movie):
    reviews: List[Review] 