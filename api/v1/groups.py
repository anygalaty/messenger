from datetime import datetime

from core.db.db import async_get_db
from fastapi import Depends, APIRouter, Request, Form, status, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from schemas.group import GroupCreate, GroupOut
from services.group_service import create_group as create_group_service, add_user_to_group, remove_user_from_group, \
    post_group_message
from core.security import require_auth, verify_token
from services.auth_service import get_user_from_cookie
from core.websocket_manager import ConnectionManager
from services.group_service import get_group_messages_payload
from api.v1.messenger import manager as messenger_manager

router = APIRouter()
manager = ConnectionManager()


@router.post("/create", response_model=GroupOut)
@require_auth
async def create_group(
        request: Request,
        name: str = Form(...),
        group_type: str = Form(...),
        participants: str = Form(...),
        db=Depends(async_get_db)
):
    creator_id = await get_user_from_cookie(request)
    participants_list = [p.strip() for p in participants.split(",") if p.strip()]
    group = GroupCreate(
        name=name,
        creator_id=creator_id,
        group_type=group_type,
        participants=participants_list
    )
    group.participants.append(creator_id)
    created_group = await create_group_service(group, db)

    for user_id in participants_list:
        if user_id != creator_id:
            await messenger_manager.send_to_user(user_id, {
                "event": "new_group",
                "group_id": created_group.id,
                "group_name": created_group.name
            })

    return RedirectResponse(url=f'/group/{created_group.id}', status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{group_id}/join")
@require_auth
async def join_group(group_id: str, request: Request, db=Depends(async_get_db)):
    user_id = await get_user_from_cookie(request)
    await add_user_to_group(group_id, user_id, db)
    return RedirectResponse(url=f"/group/{group_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{group_id}/leave")
@require_auth
async def leave_group(group_id: str, request: Request, db=Depends(async_get_db)):
    user_id = await get_user_from_cookie(request)
    await remove_user_from_group(group_id, user_id, db)
    return RedirectResponse(url=f"/group/{group_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{group_id}/post")
@require_auth
async def post_to_group(group_id: str, request: Request, text: str = Form(...), db=Depends(async_get_db)):
    user_id = await get_user_from_cookie(request)
    await post_group_message(group_id, user_id, text, db)
    return RedirectResponse(url=f"/group/{group_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.websocket("/{group_id}")
async def group_websocket(websocket: WebSocket, group_id: str, db=Depends(async_get_db)):
    token = websocket.cookies.get("access_token")
    payload = verify_token(token)
    user_id = payload.get("sub")

    await manager.connect(group_id, websocket)
    try:
        history_payload = await get_group_messages_payload(group_id, 50, db)
        await websocket.send_json(history_payload)

        while True:
            data = await websocket.receive_json()
            if data.get("event") == "post":
                text = data["text"]
                await post_group_message(group_id, user_id, text, db)

                await manager.broadcast(group_id, {
                    "event": "message",
                    "text": text,
                    "sender_name": "{{ group.name }}",
                    "created_at": datetime.utcnow().strftime("%d.%m.%Y, %H:%M")
                })

    except WebSocketDisconnect:
        await manager.disconnect(group_id, websocket)

