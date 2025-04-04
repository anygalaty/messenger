from datetime import datetime
from core.base import Base
from models.user import User
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, ForeignKey, DateTime, Enum, Table, Column, relationship
import uuid

chat_participants = Table(
    'chat_participants',
    Base.metadata,
    Column('chat_id', String, ForeignKey('chats.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True)
)


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    chat_type: Mapped[str] = mapped_column(Enum('personal', 'group'), nullable=False)
    participants: Mapped[list[User]] = relationship(
        'User',
        secondary=chat_participants,
        back_populates='chats',
        order_by=User.name,
    )
