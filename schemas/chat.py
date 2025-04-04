from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ChatType(str, Enum):
    personal = 'personal'
    group = 'group'


class ChatCreate(BaseModel):
    chat_type: ChatType = Field(...)
    participants: list[str] = Field(...)


class ChatOut(BaseModel):
    id: str = Field(...)
    created_at: datetime = Field(...)
    chat_type: ChatType = Field(...)
    participants: list[str] = Field(...)

    model_config = ConfigDict(from_attributes=True)
