from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ChatType(str, Enum):
    personal = "personal"
    group = "group"


class ChatCreate(BaseModel):
    chat_type: ChatType = Field(
        ...,
        description="Тип чата: личный (personal) или групповой (group)",
        example="personal"
    )
    participants: list[str] = Field(
        ...,
        description="Список ID участников чата",
        example=["e6f7a8a4-0e0b-4b89-a8e4-32d72ff8374b", "0b6ac1a5-5059-4c18-bdef-c9d55d1d6571"]
    )


class ChatOut(BaseModel):
    id: str = Field(
        ...,
        description="Уникальный идентификатор чата",
        example="a3f2d9f6-baa1-4a1c-92f0-8fbd77463e23"
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания чата",
        example="2025-04-07T12:34:56"
    )
    chat_type: ChatType = Field(
        ...,
        description="Тип чата (personal или group)",
        example="group"
    )
    participants: list[str] = Field(
        ...,
        description="Список ID участников чата",
        example=["e6f7a8a4-0e0b-4b89-a8e4-32d72ff8374b", "0b6ac1a5-5059-4c18-bdef-c9d55d1d6571"]
    )

    model_config = ConfigDict(from_attributes=True)
