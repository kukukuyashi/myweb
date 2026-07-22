from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_email(v: str) -> str:
    email = v.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("邮箱格式不正确，须为有效邮箱地址（含 @ 符号）")
    return email


class EmailCodeRequest(BaseModel):
    email: str = Field(max_length=255)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return _validate_email(v)


class PasswordResetRequest(BaseModel):
    email: str = Field(max_length=255)
    code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=9, max_length=128)

    @field_validator("email")
    @classmethod
    def check_email_rs(cls, v: str) -> str:
        return _validate_email(v)

    @field_validator("password")
    @classmethod
    def password_strong_rs(cls, v: str) -> str:
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", v):
            raise ValueError("密码须同时包含大写字母、小写字母和数字")
        return v


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(max_length=255)
    password: str = Field(min_length=9, max_length=128)
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    nickname: str | None = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return _validate_email(v)

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", v):
            raise ValueError("密码须同时包含大写字母、小写字母和数字")
        return v


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6, max_length=128)


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=100)
    avatar: str | None = Field(default=None, max_length=512)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=9, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", v):
            raise ValueError("密码须同时包含大写字母、小写字母和数字")
        return v


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    nickname: str
    avatar: str | None
    xp: int = 0
    level: int = 1
    checkin_streak: int = 0
    created_at: datetime


class UserProfilePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str
    avatar: str | None = None
    level: int = 1
    level_title: str = "一阶"
    xp: int = 0
    thread_count: int = 0
    created_at: datetime
