from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserCreate(BaseModel):
    name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=50)
    password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    email: EmailStr = Field(...)

    model_config = ConfigDict(from_attributes=True)
