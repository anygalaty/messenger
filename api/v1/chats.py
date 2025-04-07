from core.db.db import async_get_db
from fastapi import Depends, APIRouter, Form, status, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.chat import ChatCreate, ChatOut
from services.auth_service import get_user_from_cookie
from services.chat_service import create_chat as create_chat_service, get_chat_display_name
from core.security import require_auth
from services.message_service import (
    get_messages_history_payload,
    build_and_broadcast_message,
    notify_unread_chats,
    handle_message_read
)
from services.user_service import get_user_by_id, get_users_by_ids
from api.v1.messenger import manager as status_manager
from core.websocket_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.post(
    "/create",
    response_model=ChatOut,
    summary="Создание нового чата",
    description="Создаёт личный или групповой чат,"
                " добавляет участников и отправляет им уведомление через WebSocket."
)
@require_auth
async def create_chat(
    request: Request,
    chat_type: str = Form(..., description="Тип чата: 'personal' или 'group'"),
    participants: str = Form(..., description="Список ID участников через запятую"),
    db: AsyncSession = Depends(async_get_db)
) -> RedirectResponse:
    creator_id = await get_user_from_cookie(request)
    participants_list = [p.strip() for p in participants.split(",") if p.strip()]
    chat = ChatCreate(
        chat_type=chat_type,
        participants=participants_list,
    )
    chat.participants.append(creator_id)
    created_chat = await create_chat_service(chat, db)

    users = await get_users_by_ids(participants_list + [creator_id], db)
    name_map = {user.id: user.name for user in users}
    for user_id in participants_list:
        if user_id != creator_id:
            display_name = get_chat_display_name(
                chat_type=created_chat.chat_type.value,
                participants=created_chat.participants,
                name_map=name_map,
                for_user_id=user_id
            )
            await status_manager.send_to_user(
                user_id, {
                    "event": "new_chat",
                    "chat_id": created_chat.id,
                    "chat_name": display_name
                }
            )

    return RedirectResponse(url="/messenger", status_code=status.HTTP_303_SEE_OTHER)


@router.websocket(
    "/chat/{chat_id}",
    name="Подключение к WebSocket-чату"
)
async def chat_websocket(
    websocket: WebSocket,
    chat_id: str,
    db: AsyncSession = Depends(async_get_db)
) -> None:
    await manager.connect(chat_id, websocket)
    try:
        history_payload = await get_messages_history_payload(chat_id, 50, db)
        await websocket.send_json(history_payload)
        while True:
            data = await websocket.receive_json()
            if data.get("event") == "message":
                await build_and_broadcast_message(data, chat_id, db, manager, get_user_by_id)
                await notify_unread_chats(chat_id, data["sender_id"], db, status_manager)

            elif data.get("event") == "typing":
                user = await get_user_by_id(data["sender_id"], db)
                data["sender_name"] = user.name
                await manager.broadcast(chat_id, data, exclude=websocket)

            elif data.get("event") == "read":
                await handle_message_read(
                    user_id=data["user_id"],
                    message_id=data["message_id"],
                    chat_id=chat_id,
                    db=db,
                    chat_ws_manager=manager,
                    status_ws_manager=status_manager
                )
    except WebSocketDisconnect:
        await manager.disconnect(chat_id, websocket)
