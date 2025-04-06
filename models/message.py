import uuid
from datetime import datetime
from core.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Column
from models.chat import Chat
from models.user import User
from core.constants import MAX_MESSAGE_LENGTH


class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String, ForeignKey(Chat.id), nullable=False)
    sender_id: Mapped[str] = mapped_column(String, ForeignKey(User.id), nullable=False)
    text: Mapped[str] = mapped_column(String(MAX_MESSAGE_LENGTH), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    is_read: Mapped[Boolean] = mapped_column(Boolean, default=False)


class MessageRead(Base):
    __tablename__ = 'message_reads'
    __table_args__ = {'extend_existing': True}

    message_id = Column('message_id', ForeignKey('messages.id'), primary_key=True)
    user_id = Column('user_id', ForeignKey('users.id'), primary_key=True)
