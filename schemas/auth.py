from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email пользователя, использующийся в качестве логина",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        description="Пароль пользователя (не менее 8 символов)",
        min_length=8,
        example="s3cureP@ss"
    )


class LoginResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT access token для аутентификации пользователя",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token для обновления access токена",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
