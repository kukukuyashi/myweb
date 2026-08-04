from pathlib import Path
import time
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.db import get_db
from app.core.response import ok
from app.core.security import get_password_hash, verify_password
from app.services.image_upload import check_upload_rate, sniff_image_ext
from app.services.level_config import get_tier
from app.models.forum import ForumThread
from app.models.user import User
from app.schemas.user import PasswordChange, UserProfilePublic, UserPublic, UserUpdate

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


@router.post("/me/password", summary="修改密码")
def change_password(
    payload: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码不正确")
    if verify_password(payload.new_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="新密码不能与当前密码相同")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()
    return ok(message="密码已更新，请使用新密码登录")


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

    check_upload_rate(current_user.id, scope="avatars")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(data) > settings.max_avatar_bytes:
        raise HTTPException(status_code=400, detail="头像不能超过 2MB")

    real_ext = sniff_image_ext(data)
    if not real_ext:
        raise HTTPException(status_code=400, detail="文件不是有效的图片")
    ext = real_ext

    _remove_local_avatar(current_user.avatar)
    filename = f"{current_user.id}_{int(time.time())}{ext}"
    dest = _avatars_dir() / filename
    dest.write_bytes(data)

    current_user.avatar = f"/uploads/avatars/{filename}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return ok(UserPublic.model_validate(current_user).model_dump(), message="头像已更新")


@router.get("/{user_id}", summary="用户公开资料")
def get_user_profile(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    thread_count = db.query(ForumThread).filter(ForumThread.user_id == user_id).count()
    tier = get_tier(user.level)
    data = UserProfilePublic.model_validate(user).model_copy(
        update={"level_title": tier.title, "thread_count": thread_count}
    )
    return ok(data.model_dump())


@router.get("/{user_id}/threads", summary="用户的帖子")
def get_user_threads(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    from sqlalchemy.orm import joinedload

    from app.schemas.forum import ForumThreadListItem

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    rows = (
        db.query(ForumThread)
        .options(joinedload(ForumThread.user), joinedload(ForumThread.category))
        .filter(ForumThread.user_id == user_id)
        .order_by(ForumThread.created_at.desc())
        .limit(50)
        .all()
    )
    tier = get_tier(user.level)
    items = []
    for r in rows:
        items.append(
            ForumThreadListItem(
                id=r.id,
                category_id=r.category_id,
                category_name=r.category.name if r.category else None,
                category_slug=r.category.slug if r.category else None,
                title=r.title,
                reply_count=r.reply_count,
                view_count=r.view_count,
                like_count=r.like_count,
                is_pinned=r.is_pinned,
                is_locked=r.is_locked,
                is_featured=r.is_featured,
                cover_url=r.cover_url,
                featured_order=r.featured_order,
                created_at=r.created_at,
                updated_at=r.updated_at,
                author={
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "avatar": user.avatar,
                    "level": user.level,
                    "level_title": tier.title,
                },
            ).model_dump()
        )
    return ok({"items": items})


