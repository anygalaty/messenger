from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class LoginResponse(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
