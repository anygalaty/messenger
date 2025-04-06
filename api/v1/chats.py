from core.db.db import async_get_db
from fastapi import Depends, APIRouter
from schemas.chat import ChatCreate, ChatOut
from services.chat_service import create_chat as create_chat_service
from core.security import require_auth

router = APIRouter()


@router.post("/create", response_model=ChatOut)
@require_auth
async def create_chat(chat: ChatCreate, db=Depends(async_get_db)):
    new_chat = await create_chat_service(chat, db)
    return new_chat
