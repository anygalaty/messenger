from sqlalchemy import select, insert, delete

from core.db.db import async_get_db
from models import User
from models.message import MessageGroup
from schemas.group import GroupOut, GroupCreate
from fastapi import status, HTTPException
from models.group import Group, GroupParticipant
from schemas.message import MessageGroupOut
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


async def get_group_by_id(group_id: str, db) -> Group | HTTPException:
    stmt = select(Group).where(Group.id == group_id)
    result = await db.execute(stmt)
    group = result.unique().scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


async def add_user_to_group(group_id: str, user_id: str, db):
    stmt = select(GroupParticipant).where(
        GroupParticipant.group_id == group_id,
        GroupParticipant.user_id == user_id
    )
    result = await db.execute(stmt)
    if result.first():
        return

    await db.execute(insert(GroupParticipant).values(group_id=group_id, user_id=user_id))
    await db.commit()


async def remove_user_from_group(group_id: str, user_id: str, db):
    await db.execute(
        delete(GroupParticipant).where(
            GroupParticipant.group_id == group_id,
            GroupParticipant.user_id == user_id
        )
    )
    await db.commit()


async def post_group_message(group_id: str, sender_id: str, text: str, db):
    group = await db.scalar(select(Group).where(Group.id == group_id))
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    if group.creator_id != sender_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only creator can post")

    message = MessageGroup(
        group_id=group_id,
        sender_id=sender_id,
        text=text
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return MessageGroupOut.from_orm(message)


async def get_group_messages_payload(group_id: str, limit: int, db) -> dict:
    stmt = select(MessageGroup).where(
        MessageGroup.group_id == group_id
    ).order_by(MessageGroup.created_at.desc()).limit(limit)

    result = await db.execute(stmt)
    messages = result.scalars().all()

    return {
        "event": "history",
        "messages": [
            {
                "id": msg.id,
                "group_id": msg.group_id,
                "sender_id": msg.sender_id,
                "text": msg.text,
                "created_at": msg.created_at.strftime("%d.%m.%Y, %H:%M")
            }
            for msg in messages
        ]
    }
