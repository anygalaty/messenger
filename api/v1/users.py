from fastapi import Depends, APIRouter, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCreate, UserOut
from core.db.db import async_get_db
from services.user_service import register_user as register_user_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_303_SEE_OTHER,
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя в системе и перенаправляет на страницу входа."
)
async def register_user(
    name: str = Form(..., description="Имя пользователя"),
    email: str = Form(..., description="Электронная почта"),
    password: str = Form(..., description="Пароль"),
    db: AsyncSession = Depends(async_get_db)
) -> RedirectResponse:
    user = UserCreate(name=name, email=email, password=password)
    await register_user_service(user, db)
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
