from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from services.chat_service import get_user_chats as get_user_chats_service
from core.db.db import async_get_db
from services.auth_service import get_user_from_cookie
from core.security import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/chats", response_class=HTMLResponse)
@require_auth
async def get_user_chats(
        request: Request,
        db=Depends(async_get_db)
):
    current_user = await get_user_from_cookie(request)
    user_chats = await get_user_chats_service(current_user, db)
    return templates.TemplateResponse("chats.html", {"request": request, "chats": user_chats})
    # TODO использовать тут вебсокет
