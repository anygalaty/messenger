from core.base import Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, DateTime, ForeignKey, Table, Column
from models.user import User
from datetime import datetime

group_participants = Table(
    'group_participants',
    Base.metadata,
    Column('group_id', String, ForeignKey('groups.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True)
)


class Group(Base):
    __tablename__ = 'groups'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), default="Group")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    creator_id: Mapped[str] = mapped_column(String, ForeignKey(User.id), nullable=False)
    group_type: Mapped[str] = mapped_column(Enum('public', 'private'), default='public')
    participants: Mapped[list[User]] = relationship(
        'User',
        secondary=group_participants,
        backref='groups',
        order_by=User.name
    )
