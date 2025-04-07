from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserCreate(BaseModel):
    name: str = Field(
        ...,
        description="Имя пользователя",
        max_length=50,
        example="Andrey"
    )
    email: EmailStr = Field(
        ...,
        description="Электронная почта пользователя",
        max_length=50,
        example="andrey@example.com"
    )
    password: str = Field(
        ...,
        description="Пароль (минимум 8 символов)",
        min_length=8,
        example="supersecret123"
    )


class UserOut(BaseModel):
    id: str = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        example="b17305f3-38f2-4a57-a178-1a1f73d4135e"
    )
    name: str = Field(
        ...,
        description="Имя пользователя",
        example="Andrey"
    )
    email: EmailStr = Field(
        ...,
        description="Электронная почта пользователя",
        example="andrey@example.com"
    )

    model_config = ConfigDict(from_attributes=True)
