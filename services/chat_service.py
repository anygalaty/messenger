from fastapi import HTTPException, status
from core.db.db import async_get_db
from models.chat import Chat, ChatParticipant
from models.user import User
from sqlalchemy import select
from schemas.chat import ChatOut, ChatCreate, ChatType
from services.user_service import get_users_by_ids


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
        Chat.participants.any(User.id == user_id),
    ).order_by(Chat.id.asc())
    result = await db.execute(stmt)
    result = result.unique()
    chats = result.scalars().all()
    return [
        ChatOut(
            id=chat.id,
            created_at=chat.created_at,
            chat_type=chat.chat_type,
            participants=[u.id for u in chat.participants],
        ) for chat in chats
    ]


async def create_chat(chat: ChatCreate, db: async_get_db) -> ChatOut:
    if len(chat.participants) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough participants"
        )
    users = await get_users_by_ids(chat.participants, db)
    if len(users) != len(chat.participants):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some users not found"
        )
    new_chat = Chat(
        chat_type=ChatType.personal if len(chat.participants) == 2 else ChatType.group
    )
    db.add(new_chat)

    await db.flush()

    for user in users:
        participant = ChatParticipant(chat_id=new_chat.id, user_id=user.id)
        db.add(participant)

    await db.commit()
    await db.refresh(new_chat)

    new_chat_out = ChatOut(
        id=new_chat.id,
        created_at=new_chat.created_at,
        chat_type=new_chat.chat_type,
        participants=chat.participants,
    )

    return new_chat_out


async def get_chat_by_id(chat_id: str, db: async_get_db) -> ChatOut:
    stmt = select(Chat).where(
        Chat.id == chat_id
    )
    result = await db.execute(stmt)
    chat = result.unique().scalar_one_or_none()
    return chat


async def get_chat_participants(chat_id: str, db: async_get_db) -> list:
    stmt = select(ChatParticipant).where(
        ChatParticipant.chat_id == chat_id
    )
    result = await db.execute(stmt)
    chat_participants = result.scalars().all()
    return [cp.user_id for cp in chat_participants]


def get_chat_display_name(
    chat_type: str,
    participants: list[str],
    name_map: dict[str, str],
    for_user_id: str
) -> str:
    others = [name_map[uid] for uid in participants if uid != for_user_id]
    return f"{chat_type.capitalize()} чат с {', '.join(others)}"
