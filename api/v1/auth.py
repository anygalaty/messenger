from fastapi import Depends, APIRouter
from schemas.auth import LoginRequest, LoginResponse
from core.db.db import async_get_db
from services.auth_service import login as login_service

router = APIRouter()


@router.post('/login', response_model=LoginResponse)
async def login(login_request: LoginRequest, db=Depends(async_get_db)):
    tokens = await login_service(login_request.email, login_request.password, db)
    return tokens
