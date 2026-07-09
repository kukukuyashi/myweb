from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    nickname: str | None = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=100)
    avatar: str | None = Field(default=None, max_length=512)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    nickname: str
    avatar: str | None
    created_at: datetime
