from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.response import ok
from app.models.pomodoro import PomodoroSession
from app.models.user import User
from app.schemas.pomodoro import (
    PomodoroSessionCreate,
    PomodoroSessionListResponse,
    PomodoroSessionPublic,
    PomodoroStats,
    PomodoroTimelineDay,
    PomodoroTimelineResponse,
)

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _start_of_today() -> datetime:
    now = _utc_now_naive()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_week() -> datetime:
    today = _start_of_today()
    return today - timedelta(days=today.weekday())


@router.post("/sessions", summary="记录一次番茄钟")
def create_session(
    payload: PomodoroSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    completed_at = payload.completed_at or _utc_now_naive()
    row = PomodoroSession(
        user_id=current_user.id,
        duration_sec=payload.duration_sec,
        task_label=payload.task_label,
        reflection=payload.reflection,
        session_type=payload.session_type,
        completed_at=completed_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(
        PomodoroSessionPublic.model_validate(row).model_dump(),
        message="专注记录已保存",
    )


@router.get("/sessions", summary="我的番茄钟记录")
def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    session_type: str | None = Query(None, description="focus 或 break"),
):
    q = db.query(PomodoroSession).filter(PomodoroSession.user_id == current_user.id)
    if session_type:
        q = q.filter(PomodoroSession.session_type == session_type)
    total = q.count()
    rows = (
        q.order_by(PomodoroSession.completed_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ok(
        PomodoroSessionListResponse(
            items=[PomodoroSessionPublic.model_validate(r) for r in rows],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/stats", summary="番茄钟统计")
def pomodoro_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    today_start = _start_of_today()
    week_start = _start_of_week()
    base = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == "focus",
    )

    today_rows = base.filter(PomodoroSession.completed_at >= today_start).all()
    week_rows = base.filter(PomodoroSession.completed_at >= week_start).all()

    stats = PomodoroStats(
        today_minutes=sum(r.duration_sec for r in today_rows) // 60,
        today_sessions=len(today_rows),
        week_minutes=sum(r.duration_sec for r in week_rows) // 60,
        week_sessions=len(week_rows),
    )
    return ok(stats.model_dump())


@router.get("/timeline", summary="专注时间线（按日分组）")
def pomodoro_timeline(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(14, ge=1, le=90),
):
    since = _start_of_today() - timedelta(days=days - 1)
    rows = (
        db.query(PomodoroSession)
        .filter(
            PomodoroSession.user_id == current_user.id,
            PomodoroSession.session_type == "focus",
            PomodoroSession.completed_at >= since,
        )
        .order_by(PomodoroSession.completed_at.desc())
        .all()
    )
    grouped: dict[str, list[PomodoroSession]] = {}
    for row in rows:
        day_key = row.completed_at.strftime("%Y-%m-%d")
        grouped.setdefault(day_key, []).append(row)

    timeline_days = []
    for day_key in sorted(grouped.keys(), reverse=True):
        day_rows = grouped[day_key]
        timeline_days.append(
            PomodoroTimelineDay(
                date=day_key,
                total_minutes=sum(r.duration_sec for r in day_rows) // 60,
                sessions=[PomodoroSessionPublic.model_validate(r) for r in day_rows],
            )
        )
    return ok(PomodoroTimelineResponse(days=timeline_days).model_dump())
