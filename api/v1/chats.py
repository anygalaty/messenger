from core.db.db import async_get_db
from fastapi import Depends, APIRouter, Form, status, Request
from fastapi.responses import RedirectResponse
from schemas.chat import ChatCreate, ChatOut
from services.auth_service import get_user_from_cookie
from services.chat_service import create_chat as create_chat_service
from core.security import require_auth

router = APIRouter()


@router.post("/create", response_model=ChatOut)
@require_auth
async def create_chat(
        request: Request,
        chat_type: str = Form(...),
        participants: str = Form(...),
        db=Depends(async_get_db)
):
    creator_id = await get_user_from_cookie(request)
    participants_list = [p.strip() for p in participants.split(",") if p.strip()]
    chat = ChatCreate(
        chat_type=chat_type,
        participants=participants_list,
    )
    chat.participants.append(creator_id)
    await create_chat_service(chat, db)
    return RedirectResponse(url="/messenger", status_code=status.HTTP_303_SEE_OTHER)
