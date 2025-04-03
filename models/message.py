import uuid
from datetime import datetime
from core.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from models.chat import Chat
from models.user import User


class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String, ForeignKey(Chat.id), nullable=False)
    sender_id: Mapped[str] = mapped_column(String, ForeignKey(User.id), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    is_read: Mapped[Boolean] = mapped_column(Boolean, default=False)
