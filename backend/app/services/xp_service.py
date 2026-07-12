from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.xp import UserXpLog
from app.services.level_config import XP_ACTIONS, get_tier, level_from_xp

TZ = ZoneInfo("Asia/Shanghai")


def today() -> date:
    return datetime.now(TZ).date()


def _action_count_today(db: Session, user_id: int, action: str) -> int:
    return (
        db.query(UserXpLog)
        .filter(
            UserXpLog.user_id == user_id,
            UserXpLog.action == action,
            UserXpLog.event_date == today(),
        )
        .count()
    )


def apply_xp(
    db: Session,
    user: User,
    action: str,
    *,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> dict | None:
    cfg = XP_ACTIONS.get(action)
    if not cfg:
        return None
    if _action_count_today(db, user.id, action) >= cfg.daily_max:
        return {"xp_gained": 0, "capped": True, "action": action, "label": cfg.label}

    old_level = user.level
    user.xp += cfg.xp
    user.level = level_from_xp(user.xp)
    db.add(
        UserXpLog(
            user_id=user.id,
            action=action,
            xp_amount=cfg.xp,
            ref_type=ref_type,
            ref_id=ref_id,
            event_date=today(),
        )
    )
    db.add(user)
    tier = get_tier(user.level)
    return {
        "xp_gained": cfg.xp,
        "capped": False,
        "action": action,
        "label": cfg.label,
        "level": user.level,
        "title": tier.title,
        "is_level_up": user.level > old_level,
    }


def xp_payload(result: dict | None) -> dict | None:
    if not result or result.get("capped"):
        return None
    if result.get("xp_gained", 0) <= 0:
        return None
    msg = f"+{result['xp_gained']} XP（{result['label']}）"
    if result.get("is_level_up"):
        msg += f"，升级 Lv.{result['level']} {result['title']}！"
    return {
        "xp_gained": result["xp_gained"],
        "is_level_up": result.get("is_level_up", False),
        "level": result.get("level"),
        "title": result.get("title"),
        "message": msg,
    }
