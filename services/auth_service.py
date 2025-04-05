from datetime import timedelta
from core.config import security_settings
from core.security import verify_password, create_access_token, create_refresh_token, verify_token
from services.user_service import get_user_by_email
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse


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


def user_set_auth_cookie(tokens: dict, response):
    response.set_cookie(
        key='access_token',
        value=tokens['access_token'],
        httponly=True,
        max_age=int(timedelta(minutes=security_settings.access_token_expire_minutes).total_seconds()),
        expires=int(timedelta(minutes=security_settings.access_token_expire_minutes).total_seconds()),
    )
    response.set_cookie(
        key='refresh_token',
        value=tokens['refresh_token'],
        httponly=True,
        max_age=int(timedelta(days=security_settings.refresh_token_expire_days).total_seconds()),
        expires=int(timedelta(days=security_settings.refresh_token_expire_days).total_seconds()),
    )
    return response


async def get_user_from_cookie(request: Request):
    token = request.cookies.get('access_token')
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user id",
        )
    return user_id


def update_refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    payload = verify_token(refresh_token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user id"
        )

    new_payload = {"sub": user_id}
    new_access_token = create_access_token(new_payload)
    new_refresh_token = create_refresh_token(new_payload)

    response = JSONResponse(content={"access_token": new_access_token})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=int(timedelta(minutes=security_settings.access_token_expire_minutes).total_seconds()),
        expires=int(timedelta(minutes=security_settings.access_token_expire_minutes).total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=int(timedelta(days=security_settings.refresh_token_expire_days).total_seconds()),
        expires=int(timedelta(days=security_settings.refresh_token_expire_days).total_seconds()),
    )
    return response
