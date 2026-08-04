import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.db import get_db
from app.core.response import ok
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import (
    EmailCodeRequest,
    PasswordResetRequest,
    TokenData,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.services.email_service import send_password_reset_email, send_verification_email
from app.services.email_verify import can_send_code, generate_code, mark_send_rate, store_code, verify_code
from app.utils.rate_limit import rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

_DEV_SECRET_KEYS = {"dev-secret-change-in-production", "dev-cyinclog-local"}


def _is_dev_mode() -> bool:
    return get_settings().secret_key in _DEV_SECRET_KEYS


@router.post("/email/code", summary="发送注册邮箱验证码")
def send_email_code(request: Request, payload: EmailCodeRequest, db: Annotated[Session, Depends(get_db)]):
    rate_limit(request, scope="email_code", max_requests=3, window_sec=900)
    settings = get_settings()
    email = str(payload.email).strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已注册")

    if not can_send_code(email):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="发送过于频繁，请 60 秒后再试")

    code = generate_code()
    if not store_code(email, code):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="验证码暂无法保存，请稍后重试")
    mark_send_rate(email)

    smtp_ready = bool(settings.smtp_user and settings.smtp_password)
    if smtp_ready:
        try:
            send_verification_email(email, code)
        except Exception as exc:
            logger.exception("SMTP send failed for %s: %s", email, exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="邮件发送失败，请稍后重试") from exc
        return ok({"expires_in": 600}, message="验证码已发送，请查收邮箱（含垃圾箱）")

    if _is_dev_mode():
        logger.warning("DEV email code for %s: %s", email, code)
        return ok(
            {"expires_in": 600, "dev_code": code},
            message="开发模式：未配置 SMTP，验证码见下方或后端终端日志",
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="邮件服务未配置，请在 backend/.env 设置 SMTP_USER / SMTP_PASSWORD",
    )


@router.post("/register", summary="用户注册（需邮箱验证码）")
def register(request: Request, payload: UserRegister, db: Annotated[Session, Depends(get_db)]):
    rate_limit(request, scope="register", max_requests=3, window_sec=3600)
    email = str(payload.email).strip().lower()
    if not verify_code(email, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")

    nickname = payload.nickname or payload.username
    user = User(
        username=payload.username,
        email=email,
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
def login(request: Request, payload: UserLogin, db: Annotated[Session, Depends(get_db)]):
    rate_limit(request, scope="login", max_requests=5, window_sec=900)
    identifier = payload.username.strip()
    user = (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier.lower()))
        .first()
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号/邮箱或密码错误")

    token = create_access_token(subject=user.username, token_version=user.token_version)
    data = TokenData(access_token=token).model_dump()
    return ok(data, message="登录成功")


@router.get("/me", summary="当前登录用户")
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return ok(UserPublic.model_validate(current_user).model_dump())


@router.post("/password/code", summary="发送重置密码验证码")
def send_password_code(request: Request, payload: EmailCodeRequest, db: Annotated[Session, Depends(get_db)]):
    rate_limit(request, scope="password_code", max_requests=3, window_sec=900)
    settings = get_settings()
    email = str(payload.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()
    # 邮箱未注册时也返回成功，避免枚举用户邮箱
    if not user:
        return ok({"expires_in": 600}, message="若该邮箱已注册，验证码已发送，请查收邮箱（含垃圾箱）")

    if not can_send_code(email):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="发送过于频繁，请 60 秒后再试")

    code = generate_code()
    if not store_code(email, code):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="验证码暂无法保存，请稍后重试")
    mark_send_rate(email)

    smtp_ready = bool(settings.smtp_user and settings.smtp_password)
    if smtp_ready:
        try:
            send_password_reset_email(email, code)
        except Exception as exc:
            logger.exception("SMTP send failed for %s: %s", email, exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="邮件发送失败，请稍后重试") from exc
        return ok({"expires_in": 600}, message="验证码已发送，请查收邮箱（含垃圾箱）")

    if _is_dev_mode():
        logger.warning("DEV password reset code for %s: %s", email, code)
        return ok(
            {"expires_in": 600, "dev_code": code},
            message="开发模式：未配置 SMTP，验证码见下方或后端终端日志",
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="邮件服务未配置，请在 backend/.env 设置 SMTP_USER / SMTP_PASSWORD",
    )


@router.post("/password/reset", summary="通过邮箱验证码重置密码")
def reset_password(payload: PasswordResetRequest, db: Annotated[Session, Depends(get_db)]):
    email = str(payload.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")
    if not verify_code(email, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")

    user.password_hash = get_password_hash(payload.password)
    user.token_version += 1
    db.add(user)
    db.commit()
    return ok(message="密码已重置，请使用新密码登录")
