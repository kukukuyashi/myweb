from datetime import date, datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.response import ok
from app.models.checkin import UserCheckin
from app.models.user import User
from app.services.level_config import (
    all_tiers_public,
    calc_checkin_xp,
    get_tier,
    level_from_xp,
    level_progress,
    xp_actions_public,
)

router = APIRouter(prefix="/users/me/checkin", tags=["checkin"])

TZ = ZoneInfo("Asia/Shanghai")


def _today() -> date:
    return datetime.now(TZ).date()


def _status_payload(user: User, db: Session) -> dict:
    today = _today()
    checked_today = user.last_checkin_date == today
    progress = level_progress(user.xp, user.level)
    tier = get_tier(user.level)
    return {
        "checked_today": checked_today,
        "streak": user.checkin_streak,
        "last_checkin_date": user.last_checkin_date.isoformat() if user.last_checkin_date else None,
        "xp": user.xp,
        "level": user.level,
        "title": tier.title,
        "progress": progress,
        "tiers": all_tiers_public(),
        "xp_actions": xp_actions_public(),
    }


@router.get("/status", summary="签到状态")
def checkin_status(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(_status_payload(current_user, db))


@router.post("", summary="每日签到")
def do_checkin(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    today = _today()
    if current_user.last_checkin_date == today:
        raise HTTPException(status_code=400, detail="今日已签到")

    yesterday = today - timedelta(days=1)
    if current_user.last_checkin_date == yesterday:
        streak = current_user.checkin_streak + 1
    else:
        streak = 1

    xp_gained = calc_checkin_xp(streak)
    old_level = current_user.level
    current_user.xp += xp_gained
    current_user.level = level_from_xp(current_user.xp)
    current_user.checkin_streak = streak
    current_user.last_checkin_date = today

    row = UserCheckin(
        user_id=current_user.id,
        checkin_date=today,
        xp_gained=xp_gained,
        streak_day=streak,
    )
    db.add(row)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    tier = get_tier(current_user.level)
    is_level_up = current_user.level > old_level
    return ok(
        {
            "xp_gained": xp_gained,
            "streak": streak,
            "level": current_user.level,
            "title": tier.title,
            "is_level_up": is_level_up,
            "xp": current_user.xp,
            "progress": level_progress(current_user.xp, current_user.level),
        },
        message="签到成功" if not is_level_up else f"签到成功，升级至 Lv.{current_user.level} {tier.title}！",
    )


@router.get("/calendar", summary="签到日历")
def checkin_calendar(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    months: int = Query(3, ge=1, le=12),
):
    start = _today() - timedelta(days=months * 31)
    rows = (
        db.query(UserCheckin)
        .filter(UserCheckin.user_id == current_user.id, UserCheckin.checkin_date >= start)
        .order_by(UserCheckin.checkin_date.desc())
        .all()
    )
    dates = [r.checkin_date.isoformat() for r in rows]
    history = [
        {
            "date": r.checkin_date.isoformat(),
            "xp_gained": r.xp_gained,
            "streak_day": r.streak_day,
        }
        for r in rows
    ]
    return ok({"dates": dates, "history": history, "months": months})
