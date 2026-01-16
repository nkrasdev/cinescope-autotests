from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_CARD = "INVALID_CARD"
    ERROR = "ERROR"


class PaymentRegistryResponse(BaseModel):
    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: int
    user_id: str = Field(alias="userId")
    movie_id: int = Field(alias="movieId")
    total: int
    amount: int
    created_at: datetime = Field(alias="createdAt")
    status: PaymentStatus


class PaymentsListResponse(BaseModel):
    payments: list[PaymentResponse]
    count: int
    page: int
    page_size: int = Field(alias="pageSize")
    page_count: int = Field(alias="pageCount")
