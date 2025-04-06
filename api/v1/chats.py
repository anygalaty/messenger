from core.db.db import async_get_db
from fastapi import Depends, APIRouter, Form, status, Request, WebSocket, WebSocketDisconnect
from core.websocket_manager import ConnectionManager
from fastapi.responses import RedirectResponse
from schemas.chat import ChatCreate, ChatOut
from schemas.message import MessageCreate
from services.auth_service import get_user_from_cookie
from services.chat_service import create_chat as create_chat_service
from core.security import require_auth
from services.message_service import create_message as create_message_service, get_messages_history_payload
from services.user_service import get_user_by_id

router = APIRouter()
manager = ConnectionManager()


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


@router.websocket("/chat/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: str, db=Depends(async_get_db)):
    await manager.connect(chat_id, websocket)
    try:
        history_payload = await get_messages_history_payload(chat_id, 50, db)
        await websocket.send_json(history_payload)
        while True:
            data = await websocket.receive_json()
            if data.get("event") == "message":
                new_message = MessageCreate(
                    chat_id=chat_id,
                    sender_id=data["sender_id"],
                    text=data["text"]
                )
                new_message = await create_message_service(new_message, db)
                user = await get_user_by_id(data["sender_id"], db)
                data['sender_name'] = user.name
                data['sender_email'] = user.email
                data['created_at'] = new_message.created_at.strftime("%d.%m.%Y, %H:%M")
                await manager.broadcast(chat_id, data)
            elif data.get("event") == "typing":
                await manager.broadcast(chat_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(chat_id, websocket)
