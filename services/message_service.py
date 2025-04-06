from schemas.message import MessageOut, MessageCreate
from core.db.db import async_get_db
from models.message import Message
from fastapi import HTTPException, status
from core.constants import MAX_MESSAGE_LENGTH
from services.chat_service import check_user
from sqlalchemy import select
from services.user_service import get_users_by_ids


async def create_message(message: MessageCreate, db: async_get_db) -> MessageOut | None:
    if len(message.text) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Message too long')
    new_message = Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        text=message.text
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return MessageOut.from_orm(new_message)


async def get_messages_history(
        chat_id: str,
        user_id: str,
        limit: int,
        offset: int,
        db: async_get_db
) -> list[MessageOut]:
    await check_user(user_id, chat_id, db)
    stmt = select(Message).where(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [MessageOut.from_orm(msg) for msg in messages]


async def get_messages_history_payload(
        chat_id: str,
        limit: int,
        db: async_get_db
) -> dict:
    stmt = select(Message).where(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    user_ids = list({m.sender_id for m in messages})
    users = await get_users_by_ids(user_ids, db)
    user_map = {u.id: {"name": u.name, "email": u.email} for u in users}
    history_payload = {
        "event": "history",
        "messages": [
            {
                "id": msg.id,
                "chat_id": msg.chat_id,
                "sender_id": msg.sender_id,
                "sender_name": user_map.get(msg.sender_id, {}).get("name", "Unknown"),
                "sender_email": user_map.get(msg.sender_id, {}).get("email", ""),
                "text": msg.text,
                "created_at": msg.created_at.strftime("%d.%m.%Y, %H:%M"),
                "is_read": msg.is_read,
            }
            for msg in messages
        ]
    }

    return history_payload
