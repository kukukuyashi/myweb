"""ACG 机器人运行时设置：存 site_page_configs 表（page_key=acg_bot），零迁移。

- auto_enabled=False 时定时任务整体跳过（手动「一键生成」不受影响）
- auto_publish_daily=None 表示跟随环境变量 ACG_BOT_AUTO_PUBLISH_DAILY
- 定时任务每次跑完按 draft_retention_days 自动清理过期草稿
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.acg import AcgSubmission
from app.models.site_page_config import SitePageConfig

log = logging.getLogger("acg_bot.settings")

BOT_SETTINGS_KEY = "acg_bot"
_TZ = ZoneInfo("Asia/Shanghai")

DEFAULTS: dict[str, Any] = {
    "auto_enabled": True,
    "auto_publish_daily": None,
    "article_limit": 2,
    "draft_retention_days": 7,
}


def _row(db: Session) -> SitePageConfig | None:
    return (
        db.query(SitePageConfig)
        .filter(SitePageConfig.page_key == BOT_SETTINGS_KEY)
        .first()
    )


def load_settings(db: Session) -> dict[str, Any]:
    """DB 覆盖默认值；auto_publish_daily 为 None 时回落到环境变量。"""
    merged = dict(DEFAULTS)
    row = _row(db)
    if row and isinstance(row.content, dict):
        merged.update({k: v for k, v in row.content.items() if k in DEFAULTS})
    if merged["auto_publish_daily"] is None:
        merged["auto_publish_daily"] = get_settings().acg_bot_auto_publish_daily
    merged["auto_enabled"] = bool(merged["auto_enabled"])
    merged["auto_publish_daily"] = bool(merged["auto_publish_daily"])
    merged["article_limit"] = _clamp_int(merged["article_limit"], 0, 5, 2)
    merged["draft_retention_days"] = _clamp_int(merged["draft_retention_days"], 1, 30, 7)
    return merged


def save_settings(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    """校验并落库；返回合并后的生效设置。"""
    clean: dict[str, Any] = {}
    if "auto_enabled" in payload:
        clean["auto_enabled"] = bool(payload["auto_enabled"])
    if "auto_publish_daily" in payload:
        val = payload["auto_publish_daily"]
        clean["auto_publish_daily"] = None if val is None else bool(val)
    if "article_limit" in payload:
        clean["article_limit"] = _clamp_int(payload["article_limit"], 0, 5, 2)
    if "draft_retention_days" in payload:
        clean["draft_retention_days"] = _clamp_int(payload["draft_retention_days"], 1, 30, 7)

    row = _row(db)
    if not row:
        row = SitePageConfig(page_key=BOT_SETTINGS_KEY, content={})
        db.add(row)
    content = dict(row.content or {})
    content.update(clean)
    row.content = content
    db.commit()
    return load_settings(db)


def _clamp_int(value: Any, lo: int, hi: int, default: int) -> int:
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return default


def titles_created_today(db: Session) -> set[str]:
    """今日（Asia/Shanghai）已入队的投稿标题，用于去重防连点。"""
    start = datetime.now(_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = (
        db.query(AcgSubmission.title)
        .filter(AcgSubmission.created_at >= start.replace(tzinfo=None))
        .all()
    )
    return {r[0] for r in rows if r[0]}


def purge_old_drafts(db: Session, days: int) -> int:
    """删除 N 天前仍为 draft 的投稿，返回删除数。"""
    cutoff = datetime.now(_TZ).replace(tzinfo=None) - timedelta(days=days)
    n = (
        db.query(AcgSubmission)
        .filter(AcgSubmission.status == "draft", AcgSubmission.created_at < cutoff)
        .delete(synchronize_session=False)
    )
    db.commit()
    if n:
        log.info("acg_bot: purged %d drafts older than %d days", n, days)
    return n
