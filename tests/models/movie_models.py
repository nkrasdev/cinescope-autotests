from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional, List
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
    user_id: Optional[int] = Field(None, alias="userId")
    rating: Optional[int] = None
    text: Optional[str] = None
    hidden: Optional[bool] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    user: UserInReview

class Movie(BaseModel):
    id: int
    name: str
    description: str
    price: int
    image_url: Optional[str] = Field(None, alias="imageUrl")
    location: Location
    published: bool
    genre_id: int = Field(alias="genreId")
    genre: Genre
    created_at: datetime = Field(alias="createdAt")
    rating: float

class MovieWithReviews(Movie):
    reviews: List[Review] 