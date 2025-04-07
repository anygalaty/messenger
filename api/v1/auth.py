from fastapi import Depends, APIRouter, Form, status, Request
from fastapi.responses import RedirectResponse, Response
from schemas.auth import LoginRequest, LoginResponse
from core.db.db import async_get_db
from services.auth_service import login as login_service, user_set_auth_cookie, update_refresh_token
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    '/login',
    response_model=LoginResponse,
    summary="Аутентификация пользователя",
    description="Позволяет пользователю войти в систему, установить access и refresh"
                " токены в cookie и выполнить редирект в мессенджер."
)
async def login(
    email: str = Form(..., description="Email пользователя"),
    password: str = Form(..., description="Пароль пользователя"),
    db: AsyncSession = Depends(async_get_db)
) -> Response:
    login_request = LoginRequest(email=email, password=password)
    tokens = await login_service(login_request.email, login_request.password, db)
    response = RedirectResponse(url='/messenger', status_code=status.HTTP_303_SEE_OTHER)
    return user_set_auth_cookie(tokens, response)


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Удаляет access и refresh токены из cookie и перенаправляет на главную страницу."
)
async def logout() -> Response:
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@router.post(
    "/refresh",
    summary="Обновление access токена",
    description="Обновляет access токен с использованием refresh токена,"
                " передаваемого через cookie."
)
async def refresh_token(request: Request) -> Response:
    return update_refresh_token(request)
