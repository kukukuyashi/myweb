"""ACG 机器人定时任务：每日按 cron 生成草稿；可选自动发布速报。

- APScheduler 使用 AsyncIOScheduler，与 FastAPI 同事件循环，无需额外进程。
- 生成失败一律不抛出到上层，只写日志；避免中断 Web 服务。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.acg import AcgSubmission
from app.models.forum import ForumCategory
from app.services.acg_digest import build_daily_bundle
from app.services.acg_publish import publish_submission

log = logging.getLogger("acg_bot.scheduler")

_scheduler: AsyncIOScheduler | None = None
_TZ = ZoneInfo("Asia/Shanghai")


def _resolve_category_id(db, slug: str, fallback_id: int | None) -> int | None:
    if slug:
        cat = db.query(ForumCategory).filter(ForumCategory.slug == slug).first()
        if cat:
            return cat.id
    return fallback_id


async def run_daily_job() -> None:
    """定时任务主体：抓取 -> 入草稿 -> 可选自动发布速报。"""
    settings = get_settings()
    started = datetime.now(_TZ).isoformat()
    log.info("acg_bot cron start at %s", started)

    try:
        bundle = await build_daily_bundle(use_ai=False, article_limit=3)
    except Exception as exc:  # noqa: BLE001
        log.exception("acg_bot cron: build bundle failed: %s", exc)
        return

    db = SessionLocal()
    try:
        daily_category_id = _resolve_category_id(db, "acg-daily", None)
        article_category_id = _resolve_category_id(db, "acg-news", None)

        daily = bundle["daily"]
        sub_daily = AcgSubmission(
            title=daily["title"],
            content=daily["content_md"],
            category_id=daily_category_id,
            cover_url=daily.get("cover_url"),
            source_meta=daily.get("source_meta"),
            status="draft",
        )
        db.add(sub_daily)

        article_subs: list[AcgSubmission] = []
        for art in bundle["articles"]:
            s = AcgSubmission(
                title=art["title"],
                content=art["content_md"],
                category_id=article_category_id,
                cover_url=art.get("cover_url"),
                source_meta=art.get("source_meta"),
                status="draft",
            )
            db.add(s)
            article_subs.append(s)

        db.commit()
        db.refresh(sub_daily)
        for s in article_subs:
            db.refresh(s)

        auto_daily = settings.acg_bot_auto_publish_daily
        if auto_daily:
            try:
                thread = publish_submission(db, sub_daily)
                log.info(
                    "acg_bot cron: 速报已自动发布 thread_id=%s (subs total=%d)",
                    thread.id,
                    1 + len(article_subs),
                )
            except Exception as exc:  # noqa: BLE001
                # 发布失败保留草稿供人工审核
                db.rollback()
                log.exception("acg_bot cron: 自动发布速报失败，草稿仍在队列: %s", exc)
        else:
            log.info(
                "acg_bot cron done: %d 草稿入队（1 速报 + %d 深度文），等待人工审核",
                1 + len(article_subs),
                len(article_subs),
            )

        # 记录采集元数据到日志，便于线上排查
        try:
            meta = bundle.get("meta") or {}
            log.info("acg_bot cron meta: %s", json.dumps(meta, ensure_ascii=False))
        except Exception:  # noqa: BLE001
            pass
    finally:
        db.close()


def start_scheduler() -> None:
    """在 FastAPI lifespan 里调用；重复调用是安全的。"""
    global _scheduler
    if _scheduler is not None:
        return

    settings = get_settings()
    cron_expr = (settings.acg_bot_schedule_cron or "").strip()
    if not cron_expr:
        log.info("acg_bot scheduler disabled (ACG_BOT_SCHEDULE_CRON 为空)")
        return

    parts = cron_expr.split()
    if len(parts) != 5:
        log.warning("acg_bot scheduler: cron 表达式无效: %r", cron_expr)
        return

    minute, hour, dom, month, dow = parts
    trigger = CronTrigger(
        minute=minute,
        hour=hour,
        day=dom,
        month=month,
        day_of_week=dow,
        timezone=_TZ,
    )
    sched = AsyncIOScheduler(timezone=_TZ)
    sched.add_job(run_daily_job, trigger, id="acg_bot_daily", replace_existing=True)
    sched.start()
    _scheduler = sched
    next_run = sched.get_job("acg_bot_daily").next_run_time
    log.info("acg_bot scheduler started, cron=%s, next=%s", cron_expr, next_run)


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    try:
        _scheduler.shutdown(wait=False)
    except Exception:  # noqa: BLE001
        pass
    _scheduler = None
