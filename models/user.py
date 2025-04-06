from core.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String
import uuid


class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    chats: Mapped[list] = relationship(
        "Chat",
        secondary='chat_participants',
        back_populates="participants"
    )

    groups: Mapped[list] = relationship(
        "Group",
        secondary="group_participants",
        back_populates="participants"
    )
