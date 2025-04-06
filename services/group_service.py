from sqlalchemy import select

from core.db.db import async_get_db
from models import User
from schemas.group import GroupOut, GroupCreate
from fastapi import status, HTTPException
from models.group import Group, GroupParticipant
from services.user_service import get_users_by_ids


async def create_group(group: GroupCreate, db: async_get_db) -> GroupOut:
    users = await get_users_by_ids(group.participants, db)
    if len(users) != len(group.participants):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some users not found"
        )

    new_group = Group(
        name=group.name,
        group_type=group.group_type,
        creator_id=group.creator_id
    )
    db.add(new_group)

    await db.flush()

    for user in users:
        participant = GroupParticipant(group_id=new_group.id, user_id=user.id)
        db.add(participant)

    await db.commit()
    await db.refresh(new_group)

    new_group_out = GroupOut(
        id=new_group.id,
        name=new_group.name,
        created_at=new_group.created_at,
        participants=group.participants
    )
    return new_group_out


async def get_user_groups(user_id: str, db: async_get_db) -> list[GroupOut]:
    stmt = select(Group).where(
        Group.participants.any(User.id == user_id),
    ).order_by(Group.id.asc())
    result = await db.execute(stmt)
    result = result.unique()
    groups = result.scalars().all()
    return [
        GroupOut(
            id=group.id,
            name=group.name,
            created_at=group.created_at,
            participants=[u.id for u in group.participants],
        ) for group in groups
    ]
