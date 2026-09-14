"""留言板提交防护设置：存 site_page_configs 表（page_key=qa_board），零迁移。

- submit_enabled=False 时公开提交直接拒绝（历史留言仍正常展示）
- require_login=True 时必须带有效平台 JWT 才能留言
- min_interval_seconds 限制同一 IP 两次提交的最小间隔（0 = 不限）
- blocked_keywords 命中昵称或正文即拒绝提交
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.site_page_config import SitePageConfig

BOARD_SETTINGS_KEY = "qa_board"

DEFAULTS: dict[str, Any] = {
    "submit_enabled": True,
    "require_login": False,
    "min_interval_seconds": 15,
    "blocked_keywords": [],
}


def _row(db: Session) -> SitePageConfig | None:
    return (
        db.query(SitePageConfig)
        .filter(SitePageConfig.page_key == BOARD_SETTINGS_KEY)
        .first()
    )


def load_settings(db: Session) -> dict[str, Any]:
    """DB 覆盖默认值并做类型收敛。"""
    merged = dict(DEFAULTS)
    row = _row(db)
    if row and isinstance(row.content, dict):
        merged.update({k: v for k, v in row.content.items() if k in DEFAULTS})
    merged["submit_enabled"] = bool(merged["submit_enabled"])
    merged["require_login"] = bool(merged["require_login"])
    merged["min_interval_seconds"] = _clamp_int(merged["min_interval_seconds"], 0, 3600, 15)
    merged["blocked_keywords"] = _clean_keywords(merged["blocked_keywords"])
    return merged


def save_settings(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    """校验并落库；返回合并后的生效设置。"""
    clean: dict[str, Any] = {}
    if "submit_enabled" in payload:
        clean["submit_enabled"] = bool(payload["submit_enabled"])
    if "require_login" in payload:
        clean["require_login"] = bool(payload["require_login"])
    if "min_interval_seconds" in payload:
        clean["min_interval_seconds"] = _clamp_int(payload["min_interval_seconds"], 0, 3600, 15)
    if "blocked_keywords" in payload:
        clean["blocked_keywords"] = _clean_keywords(payload["blocked_keywords"])

    row = _row(db)
    if not row:
        row = SitePageConfig(page_key=BOARD_SETTINGS_KEY, content={})
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


def _clean_keywords(value: Any) -> list[str]:
    """字符串列表：去空白、去重、单条最长 50、最多 200 条。"""
    if not isinstance(value, list):
        return []
    seen: set[str] = set()
    out: list[str] = []
    for item in value:
        kw = str(item).strip()[:50]
        if kw and kw not in seen:
            seen.add(kw)
            out.append(kw)
    return out[:200]
