from fastapi import WebSocket, WebSocketDisconnect, Depends, APIRouter
from core.db.db import async_get_db
from core.websocket_manager import ConnectionManager
from core.security import verify_token
from services.message_service import get_unread_chats_for_user

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/read/status")
async def messenger_status_socket(websocket: WebSocket, db=Depends(async_get_db)):

    token = websocket.cookies.get("access_token")
    payload = verify_token(token)
    user_id = payload.get("sub")

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("event") == "check_unread":
                unread_chat_ids = await get_unread_chats_for_user(user_id, db)
                await websocket.send_json({
                    "event": "unread_chats",
                    "chat_ids": unread_chat_ids
                })

    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
