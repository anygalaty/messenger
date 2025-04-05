from fastapi import Depends, APIRouter, Form, status
from fastapi.responses import RedirectResponse
from schemas.user import UserCreate, UserOut
from core.db.db import async_get_db
from services.user_service import register_user as register_user_service

router = APIRouter()


@router.post('/register', response_model=UserOut)
async def register_user(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db=Depends(async_get_db)
):
    user = UserCreate(name=name, email=email, password=password)
    await register_user_service(user, db)
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
