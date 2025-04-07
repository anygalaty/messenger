from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MessageCreate(BaseModel):
    chat_id: str
    sender_id: str
    text: str


class MessageOut(BaseModel):
    id: str
    chat_id: str
    sender_id: str
    text: str
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class MessageReadSchema(BaseModel):
    message_id: str
    user_id: str


class MessageGroupCreate(BaseModel):
    group_id: str
    sender_id: str
    text: str


class MessageGroupOut(BaseModel):
    id: str
    group_id: str
    sender_id: str
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
