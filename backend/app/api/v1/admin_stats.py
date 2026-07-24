"""Admin dashboard summary — aggregate counts for the unified console."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.notes_admin import require_notes_admin
from app.core.db import get_db
from app.core.response import ok
from app.models.acg import AcgSubmission
from app.models.anime_watchlist import AnimeWatchlist
from app.models.forum import ForumReply, ForumThread
from app.models.post import Post
from app.models.qa import QaMessage
from app.models.user import User

router = APIRouter(prefix="/admin-stats", tags=["admin-stats"])


def _count(db: Session, model) -> int:
    try:
        return int(db.query(func.count(model.id)).scalar() or 0)
    except Exception:  # noqa: BLE001 - 单表统计失败不影响整体面板
        return 0


@router.get("/summary", summary="管理面板汇总统计")
def summary(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    bot_drafts = 0
    try:
        bot_drafts = int(
            db.query(func.count(AcgSubmission.id))
            .filter(AcgSubmission.status == "draft")
            .scalar()
            or 0
        )
    except Exception:  # noqa: BLE001
        bot_drafts = 0

    return ok(
        {
            "posts": _count(db, Post),
            "threads": _count(db, ForumThread),
            "replies": _count(db, ForumReply),
            "users": _count(db, User),
            "messages": _count(db, QaMessage),
            "anime": _count(db, AnimeWatchlist),
            "botDrafts": bot_drafts,
        }
    )