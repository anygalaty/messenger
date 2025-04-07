from datetime import datetime
from fastapi import (
    Depends, APIRouter, Request, Form, status,
    WebSocket, WebSocketDisconnect
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from schemas.group import GroupCreate, GroupOut
from core.db.db import async_get_db
from core.security import require_auth, verify_token
from services.auth_service import get_user_from_cookie
from services.group_service import (
    create_group as create_group_service,
    add_user_to_group,
    remove_user_from_group,
    post_group_message,
    get_group_messages_payload
)
from core.websocket_manager import ConnectionManager
from api.v1.messenger import manager as messenger_manager

router = APIRouter()
manager = ConnectionManager()


@router.post(
    "/create",
    response_model=GroupOut,
    summary="Создать новую группу",
    description="Создаёт новую группу с указанными участниками."
                " Создатель будет автоматически добавлен."
)
@require_auth
async def create_group(
    request: Request,
    name: Annotated[str, Form(description="Название группы")],
    group_type: Annotated[str, Form(description="Тип группы: 'public' или 'private'")],
    participants: Annotated[str, Form(description="ID участников через запятую")],
    db: AsyncSession = Depends(async_get_db)
) -> RedirectResponse:
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
            await messenger_manager.send_to_user(
                user_id, {
                    "event": "new_group",
                    "group_id": created_group.id,
                    "group_name": created_group.name
                }
            )

    return RedirectResponse(url=f'/group/{created_group.id}', status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    "/{group_id}/join",
    summary="Присоединиться к группе",
    description="Добавляет текущего пользователя в список участников указанной группы."
)
@require_auth
async def join_group(
    group_id: str,
    request: Request,
    db: AsyncSession = Depends(async_get_db)
) -> RedirectResponse:
    user_id = await get_user_from_cookie(request)
    await add_user_to_group(group_id, user_id, db)
    return RedirectResponse(url=f"/group/{group_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    "/{group_id}/leave",
    summary="Покинуть группу",
    description="Удаляет текущего пользователя из участников указанной группы."
)
@require_auth
async def leave_group(
    group_id: str,
    request: Request,
    db: AsyncSession = Depends(async_get_db)
) -> RedirectResponse:
    user_id = await get_user_from_cookie(request)
    await remove_user_from_group(group_id, user_id, db)
    return RedirectResponse(url=f"/group/{group_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    "/{group_id}/post",
    summary="Отправить сообщение в группу",
    description="Создатель группы может отправлять сообщения. Участники группы могут только читать."
)
@require_auth
async def post_to_group(
    group_id: str,
    request: Request,
    text: Annotated[str, Form(description="Текст сообщения")],
    db: AsyncSession = Depends(async_get_db)
) -> RedirectResponse:
    user_id = await get_user_from_cookie(request)
    await post_group_message(group_id, user_id, text, db)
    return RedirectResponse(url=f"/group/{group_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.websocket(
    "/{group_id}",
    name="WebSocket: Подписка на группу"
)
async def group_websocket(
    websocket: WebSocket,
    group_id: str,
    db: AsyncSession = Depends(async_get_db)
) -> None:
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

                await manager.broadcast(
                    group_id, {
                        "event": "message",
                        "text": text,
                        "sender_name": "{{ group.name }}",
                        "created_at": datetime.utcnow().strftime("%d.%m.%Y, %H:%M")
                    }
                )

    except WebSocketDisconnect:
        await manager.disconnect(group_id, websocket)
