from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class GroupType(str, Enum):
    public = "public"
    private = "private"


class GroupCreate(BaseModel):
    name: str = Field(
        ...,
        description="Название группы (от 1 до 50 символов)",
        min_length=1,
        max_length=50,
        example="Backend Team"
    )
    creator_id: str = Field(
        ...,
        description="ID пользователя, создавшего группу",
        example="1a2b3c4d-5678-90ab-cdef-1234567890ab"
    )
    group_type: GroupType = Field(
        ...,
        description="Тип группы: public или private",
        example="public"
    )
    participants: list[str] = Field(
        ...,
        description="Список ID участников группы",
        example=[
            "5a6a5e6c-b6d1-4f98-9c18-19a3cbbb2124",
            "7b7b9f98-e2f1-4127-b871-cb4ae13295fa"
        ]
    )


class GroupOut(BaseModel):
    id: str = Field(
        ...,
        description="Уникальный идентификатор группы",
        example="0af3218a-92bb-42f6-82fa-e637e928e097"
    )
    name: str = Field(
        ...,
        description="Название группы",
        example="Backend Team"
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания группы",
        example="2025-04-07T15:30:00"
    )
    participants: list[str] = Field(
        ...,
        description="Список ID участников группы",
        example=[
            "5a6a5e6c-b6d1-4f98-9c18-19a3cbbb2124",
            "7b7b9f98-e2f1-4127-b871-cb4ae13295fa"
        ]
    )

    model_config = ConfigDict(from_attributes=True)
