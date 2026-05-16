from datetime import datetime

from pydantic import BaseModel, Field


class SourceNotification(BaseModel):
    id: str = Field(alias="ID")
    type: str = Field(alias="Type")
    message: str = Field(alias="Message")
    timestamp: datetime = Field(alias="Timestamp")

    model_config = {
        "populate_by_name": True
    }


class RankedNotification(BaseModel):
    id: str
    type: str
    message: str
    timestamp: datetime
    is_read: bool
    priority_score: float
    priority_rank: int
    type_weight: int
    unread_bonus: int
    recency_score: float


class PriorityInboxResponse(BaseModel):
    success: bool
    message: str
    data: dict

