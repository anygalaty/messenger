from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_service import get_user_chats as get_user_chats_service
from services.group_service import (
    get_user_groups as get_user_groups_service,
    get_group_by_id as get_group_by_id_service
)
from core.db.db import async_get_db
from services.auth_service import get_user_from_cookie
from core.security import require_auth
from services.user_service import get_users_by_ids, get_user_by_id

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get(
    "/",
    response_class=HTMLResponse,
    summary="Домашняя страница",
    description="Отображает домашнюю страницу сервиса Messenger."
)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request
        }
    )


@router.get(
    "/register",
    response_class=HTMLResponse,
    summary="Страница регистрации",
    description="Отображает форму для регистрации нового пользователя."
)
async def register(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request
        }
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
    summary="Страница входа",
    description="Отображает форму авторизации пользователя."
)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )


@router.get(
    "/messenger",
    response_class=HTMLResponse,
    summary="Главная страница мессенджера",
    description="Отображает список чатов и групп текущего пользователя."
)
@require_auth
async def get_user_chats_groups(
    request: Request,
    db: AsyncSession = Depends(async_get_db)
) -> HTMLResponse:
    current_user = await get_user_from_cookie(request)
    user_chats = await get_user_chats_service(current_user, db)
    user_groups = await get_user_groups_service(current_user, db)

    chat_names = {}
    for chat in user_chats:
        users = await get_users_by_ids(chat.participants, db)
        visible_names = [u.name for u in users if u.id != current_user]
        chat_names[chat.id] = visible_names
    current_user_obj = await get_user_by_id(current_user, db)
    return templates.TemplateResponse(
        "messenger.html", {
            "request": request,
            "chats": user_chats,
            "groups": user_groups,
            "chat_names": chat_names,
            "current_user_id": current_user,
            "user_name": current_user_obj.name,
            "user_email": current_user_obj.email
        }
    )


@router.get(
    "/chat/{chat_id}",
    response_class=HTMLResponse,
    summary="Страница чата",
    description="Отображает страницу конкретного чата."
)
@require_auth
async def chat_page(
    request: Request,
    chat_id: str,
    current_user: str = Depends(get_user_from_cookie)
) -> HTMLResponse:
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "chat_id": chat_id,
            "current_user": current_user
        }
    )


@router.get(
    "/group/{group_id}",
    response_class=HTMLResponse,
    summary="Страница группы",
    description="Отображает страницу конкретной группы, включая посты и действия участников."
)
@require_auth
async def group_page(
    group_id: str,
    request: Request,
    db: AsyncSession = Depends(async_get_db)
) -> HTMLResponse:
    user_id = await get_user_from_cookie(request)
    group = await get_group_by_id_service(group_id, db)
    is_participant = user_id in [p.id for p in group.participants]
    return templates.TemplateResponse(
        "group.html", {
            "request": request,
            "group": group,
            "is_participant": is_participant,
            "is_owner": group.creator_id == user_id,
            "user_id": user_id
        }
    )
