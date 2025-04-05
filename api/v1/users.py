from fastapi import Depends, APIRouter
from schemas.user import UserCreate, UserOut
from core.db.db import async_get_db
from services.user_service import register_user as register_user_service

router = APIRouter()


@router.post('/register', response_model=UserOut)
async def register_user(user: UserCreate, db=Depends(async_get_db)):
    new_user = await register_user_service(user, db)
    return new_user
