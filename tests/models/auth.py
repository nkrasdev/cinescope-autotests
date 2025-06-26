from pydantic import BaseModel, Field
from tests.models.user import User

class LoginResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    user: User 