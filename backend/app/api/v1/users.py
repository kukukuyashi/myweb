from pathlib import Path
import time
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.db import get_db
from app.core.response import ok
from app.models.user import User
from app.schemas.user import UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/pjpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

EXT_BY_SUFFIX = {
    ".jpg": ".jpg",
    ".jpeg": ".jpg",
    ".png": ".png",
    ".webp": ".webp",
    ".gif": ".gif",
}


def _guess_ext(content_type: str, filename: str | None) -> str | None:
    ext = ALLOWED_AVATAR_TYPES.get(content_type)
    if ext:
        return ext
    if filename:
        suffix = Path(filename).suffix.lower()
        return EXT_BY_SUFFIX.get(suffix)
    return None


def _avatars_dir() -> Path:
    settings = get_settings()
    path = Path(settings.upload_dir) / "avatars"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _remove_local_avatar(avatar: str | None) -> None:
    if not avatar or not avatar.startswith("/uploads/avatars/"):
        return
    file_path = Path(get_settings().upload_dir) / "avatars" / Path(avatar).name
    if file_path.is_file():
        file_path.unlink(missing_ok=True)


@router.get("/me", summary="个人资料")
def get_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return ok(UserPublic.model_validate(current_user).model_dump())


@router.patch("/me", summary="更新个人资料")
def update_profile(
    payload: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current_user, key, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return ok(UserPublic.model_validate(current_user).model_dump(), message="更新成功")


@router.post("/me/avatar", summary="上传头像")
async def upload_avatar(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    settings = get_settings()
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    ext = _guess_ext(content_type, file.filename)
    if not ext:
        raise HTTPException(status_code=400, detail="仅支持 JPG / PNG / WebP / GIF")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(data) > settings.max_avatar_bytes:
        raise HTTPException(status_code=400, detail="头像不能超过 2MB")

    _remove_local_avatar(current_user.avatar)
    filename = f"{current_user.id}_{int(time.time())}{ext}"
    dest = _avatars_dir() / filename
    dest.write_bytes(data)

    current_user.avatar = f"/uploads/avatars/{filename}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return ok(UserPublic.model_validate(current_user).model_dump(), message="头像已更新")
