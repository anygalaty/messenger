from fastapi import Depends, APIRouter, Query
from schemas.message import MessageOut, MessageCreate
from core.db.db import async_get_db
from typing import Optional
from services.message_service import get_messages_history as get_history_service, create_message
from core.security import require_auth

router = APIRouter()


@router.post("/send", response_model=MessageOut)
@require_auth
async def send_message(
        message: MessageCreate,
        db=Depends(async_get_db)
) -> MessageOut:
    new_message = await create_message(message, db)
    return new_message


@router.get("/history/{chat_id}", response_model=list[MessageOut])
@require_auth
async def get_messages_history(
        chat_id: str,
        user_id: str,
        offset: Optional[int] = Query(0, ge=0),
        limit: Optional[int] = Query(100, ge=1),
        db=Depends(async_get_db),
) -> list[MessageOut]:
    history = await get_history_service(
        chat_id=chat_id,
        user_id=user_id,
        offset=offset,
        limit=limit,
        db=db,
    )
    return history
