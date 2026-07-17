"""ACG 资讯机器人 API：采集生成投稿、审核队列 CRUD、发布到论坛。

鉴权复用 notes_admin 的运维账号 JWT（require_notes_admin）。
"""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.notes_admin import require_notes_admin
from app.core.config import get_settings
from app.core.db import get_db
from app.core.response import ok
from app.models.acg import AcgSubmission
from app.models.forum import ForumCategory
from app.services.acg_digest import build_daily_bundle, polish_with_dify
from app.services.acg_publish import publish_submission
from app.services.notes_markdown import markdown_to_html
from pydantic import BaseModel

router = APIRouter(prefix="/acg-bot", tags=["acg-bot"])


class GenerateBody(BaseModel):
    use_ai: bool = False
    category_id: int | None = None
    article_limit: int = 3


class SubmissionUpdateBody(BaseModel):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None
    cover_url: str | None = None


def _front_thread_url(thread_id: int) -> str:
    settings = get_settings()
    base = (settings.public_site_url or "").rstrip("/")
    return f"{base}/app/forum/t/{thread_id}"


def _serialize(sub: AcgSubmission, *, with_source: bool = False) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": sub.id,
        "title": sub.title,
        "content": sub.content,
        "category_id": sub.category_id,
        "cover_url": sub.cover_url,
        "status": sub.status,
        "published_thread_id": sub.published_thread_id,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
        "updated_at": sub.updated_at.isoformat() if sub.updated_at else None,
    }
    if with_source:
        try:
            data["source_meta"] = json.loads(sub.source_meta) if sub.source_meta else None
        except (json.JSONDecodeError, TypeError):
            data["source_meta"] = None
    return data


def _get_or_404(db: Session, submission_id: int) -> AcgSubmission:
    sub = db.query(AcgSubmission).filter(AcgSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="投稿不存在")
    return sub


def _resolve_category_id(db: Session, slug: str, fallback_id: int | None) -> int | None:
    """按 slug 找板块 id；找不到返回 fallback_id（可能是 None，发布时再兜底）。"""
    if slug:
        cat = db.query(ForumCategory).filter(ForumCategory.slug == slug).first()
        if cat:
            return cat.id
    return fallback_id


@router.post("/generate", summary="一键采集：1 篇速报 + N 篇深度文章")
async def generate(
    body: GenerateBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    bundle = await build_daily_bundle(use_ai=body.use_ai, article_limit=body.article_limit)

    daily_category_id = _resolve_category_id(db, "acg-daily", body.category_id)
    article_category_id = _resolve_category_id(db, "acg-news", body.category_id)

    created: list[AcgSubmission] = []

    # 1 篇速报
    daily = bundle["daily"]
    daily_content_md = daily["content_md"]
    if body.use_ai:
        daily_content_md = await polish_with_dify(daily["title"], daily_content_md)
    sub_daily = AcgSubmission(
        title=daily["title"],
        content=daily_content_md,
        category_id=daily_category_id,
        cover_url=daily.get("cover_url"),
        source_meta=daily.get("source_meta"),
        status="draft",
    )
    db.add(sub_daily)
    created.append(sub_daily)

    # N 篇深度文章
    for art in bundle["articles"]:
        sub = AcgSubmission(
            title=art["title"],
            content=art["content_md"],
            category_id=article_category_id,
            cover_url=art.get("cover_url"),
            source_meta=art.get("source_meta"),
            status="draft",
        )
        db.add(sub)
        created.append(sub)

    db.commit()
    for s in created:
        db.refresh(s)

    return ok(
        {
            "submissions": [_serialize(s, with_source=True) for s in created],
            "meta": bundle["meta"],
        },
        message=f"已生成 1 篇速报 + {len(created) - 1} 篇深度文章",
    )


@router.get("/submissions", summary="投稿列表")
def list_submissions(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
    status: str = Query("all"),
):
    q = db.query(AcgSubmission)
    if status and status != "all":
        q = q.filter(AcgSubmission.status == status)
    rows = q.order_by(AcgSubmission.created_at.desc(), AcgSubmission.id.desc()).all()
    return ok({"submissions": [_serialize(r) for r in rows]})


@router.get("/submissions/{submission_id}", summary="投稿详情（含来源核对）")
def get_submission(
    submission_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    sub = _get_or_404(db, submission_id)
    return ok(_serialize(sub, with_source=True))


@router.put("/submissions/{submission_id}", summary="编辑草稿")
def update_submission(
    submission_id: int,
    body: SubmissionUpdateBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    sub = _get_or_404(db, submission_id)
    if sub.status == "published":
        raise HTTPException(status_code=400, detail="已发布投稿不可编辑")

    if body.title is not None:
        sub.title = body.title
    if body.content is not None:
        sub.content = body.content
    if body.category_id is not None:
        sub.category_id = body.category_id or None
    if body.cover_url is not None:
        sub.cover_url = body.cover_url or None
    db.commit()
    db.refresh(sub)
    return ok(_serialize(sub, with_source=True))


@router.post("/submissions/{submission_id}/preview", summary="Markdown 预览")
def preview_submission(
    submission_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    sub = _get_or_404(db, submission_id)
    return ok({"html": markdown_to_html(sub.content or "")})


@router.post("/submissions/{submission_id}/publish", summary="发布到论坛")
def publish(
    submission_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    sub = _get_or_404(db, submission_id)
    try:
        thread = publish_submission(db, sub)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ok(
        {
            "thread_id": thread.id,
            "url": _front_thread_url(thread.id),
            "submission": _serialize(sub),
        },
        message="已发布到论坛",
    )


@router.delete("/submissions/{submission_id}", summary="丢弃草稿")
def discard(
    submission_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    sub = _get_or_404(db, submission_id)
    if sub.status == "published":
        raise HTTPException(status_code=400, detail="已发布投稿不可丢弃")
    sub.status = "discarded"
    db.commit()
    return ok({"id": sub.id, "status": sub.status}, message="已丢弃")


@router.get("/categories", summary="论坛板块列表（发布目标）")
def categories(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    rows = db.query(ForumCategory).order_by(ForumCategory.sort_order, ForumCategory.id).all()
    return ok(
        {
            "categories": [
                {"id": c.id, "name": c.name, "slug": c.slug} for c in rows
            ]
        }
    )
