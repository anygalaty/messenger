from fastapi import HTTPException, status
from core.db.db import async_get_db
from models.chat import Chat
from models.user import User
from sqlalchemy import select
from schemas.chat import ChatOut


async def check_user(user_id: str, chat_id: str, db: async_get_db) -> Chat | None:
    stmt = select(Chat).where(
        Chat.id == chat_id,
        Chat.participants.has(User.id == user_id),
    )
    result = await db.execute(stmt)
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat not found or user is not a participant in this chat",
        )
    return chat


async def get_user_chats(user_id: str, db: async_get_db) -> list[ChatOut]:
    stmt = select(Chat).where(
        Chat.participants.has(User.id == user_id),
    ).order_by(Chat.id.desc())
    result = await db.execute(stmt)
    chats = result.scalars().all()
    return [ChatOut.from_orm(chat) for chat in chats]
