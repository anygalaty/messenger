from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.db import async_get_db
from schemas.user import UserCreate
from schemas.chat import ChatCreate
from schemas.group import GroupCreate
from schemas.message import MessageCreate
from services.user_service import register_user, get_user_by_email
from services.chat_service import create_chat
from services.group_service import create_group, post_group_message
from services.message_service import create_message

router = APIRouter()


@router.post(
    "/test-data",
    summary="Создание тестовых данных",
    description="Создаёт тестовых пользователей, чаты, группы и сообщения"
)
async def create_test_data(db: AsyncSession = Depends(async_get_db)):
    users_data = [
        UserCreate(name="Андрей", email="a@example.com", password="password123"),
        UserCreate(name="Борис", email="b@example.com", password="password123"),
        UserCreate(name="Саша", email="s@example.com", password="password123")
    ]

    created_users = []
    for u in users_data:
        existing = await get_user_by_email(u.email, db)
        if not existing:
            user = await register_user(u, db)
            created_users.append(user)
        else:
            created_users.append(existing)

    user1, user2, user3 = created_users[0].id, created_users[1].id, created_users[2].id

    chat = ChatCreate(
        chat_type="personal",
        participants=[user1, user2]
    )
    created_chat = await create_chat(chat, db)

    await create_message(
        MessageCreate(
            chat_id=created_chat.id,
            sender_id=user1,
            text="Привет, Борис!"
        ), db
    )

    await create_message(
        MessageCreate(
            chat_id=created_chat.id,
            sender_id=user2,
            text="Привет, Андрей! Как дела?"
        ), db
    )

    group = GroupCreate(
        name="Test Group",
        creator_id=user1,
        group_type='public',
        participants=[user1, user3]
    )
    created_group = await create_group(group, db)

    await post_group_message(created_group.id, user1, "Добро пожаловать в группу!", db)

    return {
        "message": "Тестовые данные успешно созданы"
    }
