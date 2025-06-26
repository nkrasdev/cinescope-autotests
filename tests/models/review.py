from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from tests.models.user import UserInReview


class Review(BaseModel):
    user_id: Optional[int] = Field(None, alias="userId")
    rating: Optional[int] = None
    text: Optional[str] = None
    hidden: Optional[bool] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    user: UserInReview 