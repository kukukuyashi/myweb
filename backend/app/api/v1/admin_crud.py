"""通用管理 CRUD API — 统一控制台数据管理页的原生实现（阶段一 4 张表）。

只对 4 张表暴露白名单式的读/改/删接口；博客文章、论坛板块暂留 SQLAdmin。
鉴权复用 notes_admin JWT（require_notes_admin）。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.api.v1.notes_admin import require_notes_admin
from app.core.db import get_db
from app.core.response import ok
from app.models.forum import ForumReply, ForumThread
from app.models.qa import QaMessage
from app.models.user import User

router = APIRouter(prefix="/admin/crud", tags=["admin-crud"])


class BulkDeleteBody(BaseModel):
    ids: list[int]


# ---------------------- 资源配置 ---------------------- #

RESOURCES: dict[str, dict[str, Any]] = {
    "users": {
        "model": User,
        "searchable": ["username", "email", "nickname"],
        "editable": [
            "nickname",
            "level",
            "xp",
            "checkin_streak",
            "last_checkin_date",
        ],
        "fields": [
            "id",
            "username",
            "email",
            "nickname",
            "avatar",
            "xp",
            "level",
            "checkin_streak",
            "last_checkin_date",
            "created_at",
            "updated_at",
        ],
    },
    "threads": {
        "model": ForumThread,
        "searchable": ["title", "content"],
        "editable": [
            "title",
            "content",
            "category_id",
            "is_pinned",
            "is_locked",
            "is_featured",
            "cover_url",
            "featured_order",
            "view_count",
            "like_count",
            "share_count",
        ],
        "fields": [
            "id",
            "category_id",
            "user_id",
            "title",
            "content",
            "reply_count",
            "view_count",
            "like_count",
            "share_count",
            "is_pinned",
            "is_locked",
            "is_featured",
            "cover_url",
            "featured_order",
            "created_at",
            "updated_at",
        ],
    },
    "replies": {
        "model": ForumReply,
        "searchable": ["content"],
        "editable": ["content"],
        "fields": [
            "id",
            "thread_id",
            "user_id",
            "content",
            "like_count",
            "created_at",
        ],
    },
    "qa": {
        "model": QaMessage,
        "searchable": ["name", "content"],
        "editable": ["name", "content"],
        "fields": ["id", "name", "content", "created_at"],
    },
}


def _resource(name: str) -> dict[str, Any]:
    if name not in RESOURCES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未知资源")
    return RESOURCES[name]


def _serialize(row: Any, fields: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for f in fields:
        value = getattr(row, f, None)
        if isinstance(value, (datetime, date)):
            data[f] = value.isoformat()
        else:
            data[f] = value
    return data


def _coerce_value(model: Any, field: str, value: Any) -> Any:
    """按列类型做最小转换：日期字符串 → date，布尔值宽松解析。"""
    col = getattr(model, field, None)
    if col is None:
        return value
    try:
        col_type = col.type.python_type  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        return value

    if value is None or value == "":
        # 允许把可空字段清空
        return None

    if col_type is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        return str(value).strip().lower() in {"1", "true", "yes", "on"}
    if col_type is int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=f"字段 {field} 需要整数") from exc
    if col_type is date and not isinstance(value, date):
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"字段 {field} 日期格式应为 YYYY-MM-DD") from exc
    return value


# ---------------------- 路由 ---------------------- #


@router.get("/{resource}", summary="资源列表（分页 / 搜索 / 排序）")
def list_resource(
    resource: str,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    pageSize: Annotated[int, Query(ge=1, le=200)] = 20,
    q: str = "",
    sort: str = "-id",
):
    cfg = _resource(resource)
    model = cfg["model"]

    query = db.query(model)

    q_stripped = (q or "").strip()
    if q_stripped:
        keyword = f"%{q_stripped}%"
        clauses = [getattr(model, f).ilike(keyword) for f in cfg["searchable"]]
        if clauses:
            query = query.filter(or_(*clauses))

    # 排序：`-field` 倒序，`field` 正序
    sort_field = (sort or "-id").strip()
    direction = desc if sort_field.startswith("-") else asc
    sort_col_name = sort_field.lstrip("-+")
    if sort_col_name not in cfg["fields"]:
        sort_col_name = "id"
        direction = desc
    query = query.order_by(direction(getattr(model, sort_col_name)))

    total = query.count()
    rows = query.offset((page - 1) * pageSize).limit(pageSize).all()
    items = [_serialize(r, cfg["fields"]) for r in rows]

    return ok(
        {
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "fields": cfg["fields"],
            "editable": cfg["editable"],
            "searchable": cfg["searchable"],
        }
    )


@router.get("/{resource}/{item_id}", summary="资源详情")
def get_resource(
    resource: str,
    item_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    cfg = _resource(resource)
    row = db.query(cfg["model"]).filter(cfg["model"].id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ok(_serialize(row, cfg["fields"]))


@router.patch("/{resource}/{item_id}", summary="更新资源（白名单字段）")
def update_resource(
    resource: str,
    item_id: int,
    payload: dict[str, Any],
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    cfg = _resource(resource)
    model = cfg["model"]
    row = db.query(model).filter(model.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")

    changed: list[str] = []
    for key, value in (payload or {}).items():
        if key not in cfg["editable"]:
            continue
        setattr(row, key, _coerce_value(model, key, value))
        changed.append(key)

    if not changed:
        raise HTTPException(status_code=400, detail="没有可更新的字段")

    db.commit()
    db.refresh(row)
    return ok(_serialize(row, cfg["fields"]), message=f"已更新 {len(changed)} 个字段")


@router.delete("/{resource}/{item_id}", summary="删除资源")
def delete_resource(
    resource: str,
    item_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    cfg = _resource(resource)
    model = cfg["model"]
    row = db.query(model).filter(model.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(row)
    db.commit()
    return ok({"id": item_id, "deleted": True})


@router.post("/{resource}/bulk-delete", summary="批量删除资源")
def bulk_delete_resource(
    resource: str,
    body: BulkDeleteBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    cfg = _resource(resource)
    model = cfg["model"]
    ids = list({int(i) for i in body.ids if i})
    if not ids:
        raise HTTPException(status_code=400, detail="ids 不能为空")

    rows = db.query(model).filter(model.id.in_(ids)).all()
    for row in rows:
        db.delete(row)
    db.commit()
    return ok({"deleted": [row.id for row in rows], "requested": ids})