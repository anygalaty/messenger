from core.security import verify_password, create_access_token, create_refresh_token, hash_password
from services.user_service import get_user_by_email
from fastapi import HTTPException, status


async def authenticate_user(email, password, db):
    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password')

    return user


async def login(email, password, db):
    user = await authenticate_user(email, password, db)
    payload = {'sub': user.id}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return {'access_token': access_token, 'refresh_token': refresh_token}
