import jwt
from datetime import datetime, timedelta
from core.config import security_settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=security_settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, security_settings.secret_key, algorithm=security_settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=security_settings.refresh_token_expire_days)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, security_settings.secret_key, algorithm=security_settings.algorithm)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, security_settings.secret_key, algorithms=[security_settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token is expired')
    except jwt.InvalidTokenError:
        raise Exception('Token is invalid')


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
