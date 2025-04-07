from fastapi import Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.message import MessageOut, MessageCreate
from core.db.db import async_get_db
from services.message_service import get_messages_history as get_history_service, create_message
from core.security import require_auth

router = APIRouter()


@router.post(
    "/send",
    response_model=MessageOut,
    summary="Отправить сообщение",
    description="Создаёт и сохраняет новое сообщение в указанном чате."
)
@require_auth
async def send_message(
    message: MessageCreate,
    db: AsyncSession = Depends(async_get_db)
) -> MessageOut:
    new_message = await create_message(message, db)
    return new_message


@router.get(
    "/history/{chat_id}",
    response_model=list[MessageOut],
    summary="Получить историю сообщений",
    description="Возвращает сообщения указанного чата с поддержкой пагинации."
)
@require_auth
async def get_messages_history(
    chat_id: str,
    user_id: str,
    offset: int = Query(0, ge=0, description="Смещение от начала истории сообщений"),
    limit: int = Query(100, ge=1, description="Максимальное количество сообщений для получения"),
    db: AsyncSession = Depends(async_get_db)
) -> list[MessageOut]:
    history = await get_history_service(
        chat_id=chat_id,
        user_id=user_id,
        offset=offset,
        limit=limit,
        db=db,
    )
    return history
