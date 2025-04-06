from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class GroupType(str, Enum):
    public = "public"
    private = "private"


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    creator_id: str = Field(...)
    group_type: GroupType = Field(...)
    participants: list[str]


class GroupOut(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    created_at: datetime = Field(...)
    participants: list[str] = Field(...)
    model_config = ConfigDict(from_attributes=True)
