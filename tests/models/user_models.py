from datetime import datetime

from pydantic import Field

from tests.models.base import ApiModel


class UserInReview(ApiModel):
    full_name: str = Field(alias="fullName")


class UserDetails(ApiModel):
    email: str
    full_name: str = Field(alias="fullName")
    roles: list[str]
    verified: bool
    banned: bool = False
    created_at: datetime = Field(alias="createdAt")


class User(UserDetails):
    id: str


class UpdatedUser(UserDetails):
    """User fields returned by PATCH /user/{id}; the API omits the identifier."""


class UserSummary(ApiModel):
    id: str
    email: str
    full_name: str = Field(alias="fullName")
    roles: list[str]
