from core.base import Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, DateTime, ForeignKey, Column
from models.user import User
from datetime import datetime


class Group(Base):
    __tablename__ = 'groups'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), default="Group")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    creator_id: Mapped[str] = mapped_column(String, ForeignKey(User.id), nullable=False)
    group_type: Mapped[str] = mapped_column(Enum('public', 'private', name='group_type_enum'), default='public')
    participants: Mapped[list[User]] = relationship(
        'User',
        secondary='group_participants',
        back_populates='groups',
        order_by='User.name',
        lazy='joined'
    )


class GroupParticipant(Base):
    __tablename__ = 'group_participants'
    __table_args__ = {'extend_existing': True}
    group_id = Column('group_id', String, ForeignKey('groups.id'), primary_key=True)
    user_id = Column('user_id', String, ForeignKey('users.id'), primary_key=True)
