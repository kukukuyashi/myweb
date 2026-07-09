from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.response import ok
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import TokenData, UserLogin, UserPublic, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", summary="用户注册")
def register(payload: UserRegister, db: Annotated[Session, Depends(get_db)]):
    nickname = payload.nickname or payload.username
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        nickname=nickname,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名或邮箱已存在") from exc
    db.refresh(user)
    return ok(UserPublic.model_validate(user).model_dump(), message="注册成功")


@router.post("/login", summary="用户登录")
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = create_access_token(subject=user.username)
    data = TokenData(access_token=token).model_dump()
    return ok(data, message="登录成功")


@router.get("/me", summary="当前登录用户")
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return ok(UserPublic.model_validate(current_user).model_dump())
