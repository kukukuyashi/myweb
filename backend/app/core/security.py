import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    subject: str,
    expires_minutes: int | None = None,
    *,
    token_version: int = 0,
    extra_claims: dict | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload: dict = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "jti": uuid.uuid4().hex,
        "ver": token_version,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_notes_admin_token(username: str) -> str:
    settings = get_settings()
    return create_access_token(
        username,
        expires_minutes=settings.notes_admin_token_expire_minutes,
        extra_claims={"typ": "notes_admin"},
    )
