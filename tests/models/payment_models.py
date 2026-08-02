from datetime import datetime
from enum import Enum

from pydantic import Field

from tests.models.base import ApiModel


class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_CARD = "INVALID_CARD"
    ERROR = "ERROR"


class PaymentResult(ApiModel):
    status: PaymentStatus


class PaymentResponse(ApiModel):
    id: int
    user_id: str = Field(alias="userId")
    movie_id: int = Field(alias="movieId")
    total: int
    amount: int
    created_at: datetime = Field(alias="createdAt")
    status: PaymentStatus


class PaymentsPage(ApiModel):
    payments: list[PaymentResponse]
    count: int
    page: int
    page_size: int = Field(alias="pageSize")
    page_count: int = Field(alias="pageCount")
