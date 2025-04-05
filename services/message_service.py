from schemas.message import MessageOut, MessageCreate
from core.db.db import async_get_db
from models.message import Message
from fastapi import HTTPException, status
from core.constants import MAX_MESSAGE_LENGTH
from services.chat_service import check_user
from sqlalchemy import select


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
