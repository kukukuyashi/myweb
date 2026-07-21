from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.response import ok
from app.models.forum import ForumThread
from app.models.notification import Notification
from app.models.user import User
from app.schemas.forum import ForumAuthor
from app.schemas.notification import NotificationItem, NotificationListResponse
from app.services.level_config import get_tier

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _actor_dict(user: User | None) -> ForumAuthor | None:
    if not user:
        return None
    tier = get_tier(user.level)
    return ForumAuthor(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        avatar=user.avatar,
        level=user.level,
        level_title=tier.title,
    )


def _unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .count()
    )


@router.get("/unread-count", summary="未读通知数")
def unread_count(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok({"unread": _unread_count(db, current_user.id)})


@router.get("", summary="通知列表")
def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    q = (
        db.query(Notification)
        .options(joinedload(Notification.actor), joinedload(Notification.thread))
        .filter(Notification.user_id == current_user.id)
    )
    total = q.count()
    rows = (
        q.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        NotificationItem(
            id=n.id,
            type=n.type,
            is_read=n.is_read,
            created_at=n.created_at,
            actor=_actor_dict(n.actor),
            thread_id=n.thread_id,
            reply_id=n.reply_id,
            thread_title=n.thread.title if n.thread else None,
        )
        for n in rows
    ]
    return ok(
        NotificationListResponse(
            items=items,
            total=total,
            unread=_unread_count(db, current_user.id),
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.post("/{note_id}/read", summary="标记单条已读")
def mark_read(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    note = (
        db.query(Notification)
        .filter(Notification.id == note_id, Notification.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="通知不存在")
    note.is_read = True
    db.add(note)
    db.commit()
    return ok({"unread": _unread_count(db, current_user.id)})


@router.post("/read-all", summary="全部标记已读")
def mark_all_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read.is_(False)
    ).update({Notification.is_read: True})
    db.commit()
    return ok({"unread": 0})