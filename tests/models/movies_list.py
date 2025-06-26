from typing import List
from pydantic import BaseModel, Field
from tests.models.movie import Movie

class MoviesList(BaseModel):
    movies: List[Movie]
    page: int
    page_size: int = Field(alias="pageSize")
    count: int
    page_count: int = Field(alias="pageCount") 