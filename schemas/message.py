from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class MessageCreate(BaseModel):
    chat_id: str = Field(
        ...,
        description="ID чата, в который отправляется сообщение",
        example="c91f9e5b-4832-41cd-8702-730f58a5e9e2"
    )
    sender_id: str = Field(
        ...,
        description="ID пользователя, отправляющего сообщение",
        example="f1452dc4-6b6d-42c6-b1b9-fd5b2f6a8491"
    )
    text: str = Field(
        ...,
        description="Текст сообщения",
        example="Привет, как дела?"
    )


class MessageOut(BaseModel):
    id: str = Field(
        ...,
        description="Уникальный идентификатор сообщения",
        example="31bfa849-50c0-4c33-bf96-b01e88f63287"
    )
    chat_id: str = Field(
        ...,
        description="ID чата, к которому относится сообщение",
        example="c91f9e5b-4832-41cd-8702-730f58a5e9e2"
    )
    sender_id: str = Field(
        ...,
        description="ID отправителя сообщения",
        example="f1452dc4-6b6d-42c6-b1b9-fd5b2f6a8491"
    )
    text: str = Field(
        ...,
        description="Текст сообщения",
        example="Привет, как дела?"
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время отправки сообщения",
        example="2025-04-07T17:45:00"
    )
    is_read: bool = Field(
        ...,
        description="Флаг, прочитано ли сообщение",
        example=True
    )

    model_config = ConfigDict(from_attributes=True)


class MessageReadSchema(BaseModel):
    message_id: str = Field(
        ...,
        description="ID прочитанного сообщения",
        example="31bfa849-50c0-4c33-bf96-b01e88f63287"
    )
    user_id: str = Field(
        ...,
        description="ID пользователя, прочитавшего сообщение",
        example="f1452dc4-6b6d-42c6-b1b9-fd5b2f6a8491"
    )


class MessageGroupCreate(BaseModel):
    group_id: str = Field(
        ...,
        description="ID группы, в которую отправляется сообщение",
        example="ac99280f-53d4-40b5-baf5-f2067e138681"
    )
    sender_id: str = Field(
        ...,
        description="ID пользователя, отправляющего сообщение в группу",
        example="f1452dc4-6b6d-42c6-b1b9-fd5b2f6a8491"
    )
    text: str = Field(
        ...,
        description="Текст сообщения",
        example="Объявляю митинг в 15:00!"
    )


class MessageGroupOut(BaseModel):
    id: str = Field(
        ...,
        description="Уникальный идентификатор сообщения в группе",
        example="78d18821-1ab6-4cbf-bf64-1350eeb83a8e"
    )
    group_id: str = Field(
        ...,
        description="ID группы, в которой находится сообщение",
        example="ac99280f-53d4-40b5-baf5-f2067e138681"
    )
    sender_id: str = Field(
        ...,
        description="ID пользователя, отправившего сообщение",
        example="f1452dc4-6b6d-42c6-b1b9-fd5b2f6a8491"
    )
    text: str = Field(
        ...,
        description="Текст сообщения",
        example="Объявляю митинг в 15:00!"
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания сообщения",
        example="2025-04-07T18:15:00"
    )

    model_config = ConfigDict(from_attributes=True)
