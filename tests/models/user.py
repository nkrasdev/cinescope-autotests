from datetime import datetime

from pydantic import BaseModel, Field


class UserInReview(BaseModel):
    full_name: str = Field(alias="fullName")


class User(BaseModel):
    id: str
    email: str
    full_name: str = Field(alias="fullName")
    roles: list[str]
    verified: bool
    banned: bool
    created_at: datetime = Field(alias="createdAt") 