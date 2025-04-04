from fastapi import Depends, HTTPException, status, APIRouter
from models.user import User
from schemas.user import UserCreate, UserOut
from core.db.db import async_get_db

router = APIRouter()


@router.post('/register', response_model=UserOut)
async def register_user(user: UserCreate, db=Depends(async_get_db)):
    # check_email
    # if check_email:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f'User with email {user.email} already exists'
    #     ) # TODO - переместить логику создания юзера и проверки в service
    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserOut.from_orm(new_user)
