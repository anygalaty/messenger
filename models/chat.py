from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
import uuid
from models.user import User
from sqlalchemy import ForeignKey, String, Column, DateTime, Enum
from core.base import Base


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    chat_type: Mapped[str] = mapped_column(Enum('personal', 'group', name='chat_type_enum'), nullable=False)
    participants: Mapped[list[User]] = relationship(
        'User',
        secondary='chat_participants',
        back_populates='chats',
        order_by='User.name',
        lazy='joined'
    )


class ChatParticipant(Base):
    __tablename__ = 'chat_participants'
    __table_args__ = {'extend_existing': True}

    chat_id = Column('chat_id', String, ForeignKey('chats.id'), primary_key=True)
    user_id = Column('user_id', String, ForeignKey('users.id'), primary_key=True)
