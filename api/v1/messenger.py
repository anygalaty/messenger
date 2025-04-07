from fastapi import WebSocket, WebSocketDisconnect, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.db import async_get_db
from core.websocket_manager import ConnectionManager
from core.security import verify_token
from services.group_service import get_user_groups
from services.message_service import get_unread_chats_for_user

router = APIRouter()
manager = ConnectionManager()


@router.websocket(
    "/read/status",
    name="WebSocket: статус непрочитанных сообщений",
)
async def messenger_status_socket(
    websocket: WebSocket,
    db: AsyncSession = Depends(async_get_db)
) -> None:
    token: str = websocket.cookies.get("access_token")
    payload = verify_token(token)
    user_id: str = payload.get("sub")

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("event") == "check_unread":
                unread_chat_ids = await get_unread_chats_for_user(user_id, db)
                await websocket.send_json(
                    {
                        "event": "unread_chats",
                        "chat_ids": unread_chat_ids
                    }
                )
            elif data.get("event") == "check_groups":
                user_groups = await get_user_groups(user_id, db)
                await websocket.send_json(
                    {
                        "event": "unread_groups",
                        "group_ids": [g.id for g in user_groups]
                    }
                )
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
