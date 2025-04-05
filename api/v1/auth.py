from fastapi import Depends, APIRouter, Form, status, Request
from fastapi.responses import RedirectResponse
from schemas.auth import LoginRequest, LoginResponse
from core.db.db import async_get_db
from services.auth_service import login as login_service, user_set_auth_cookie, update_refresh_token

router = APIRouter()


@router.post('/login', response_model=LoginResponse)
async def login(
        email: str = Form(...),
        password: str = Form(...),
        db=Depends(async_get_db)
):
    login_request = LoginRequest(email=email, password=password)
    tokens = await login_service(login_request.email, login_request.password, db)
    response = RedirectResponse(url='/chats', status_code=status.HTTP_303_SEE_OTHER)
    response_with_cookie = user_set_auth_cookie(tokens, response)
    return response_with_cookie


@router.post("/logout")
async def logout():
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@router.post("/refresh")
async def refresh_token(request: Request):
    return update_refresh_token(request)
