from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.notes_admin import require_notes_admin
from app.core.db import get_db
from app.core.response import ok
from app.models.friend_link import FriendLink

router = APIRouter(prefix="/friend-links", tags=["friend-links"])


class LinkBody(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    url: str = Field(min_length=1, max_length=512)
    image_url: str | None = None
    description: str | None = None
    category: str | None = None
    sort_order: int | None = None


class LinkUpdateBody(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    url: str | None = Field(default=None, max_length=512)
    image_url: str | None = None
    description: str | None = None
    category: str | None = None
    sort_order: int | None = None


def _serialize(x: FriendLink) -> dict:
    return {
        "id": x.id,
        "name": x.name,
        "url": x.url,
        "image_url": x.image_url or "",
        "description": x.description or "",
        "category": x.category or "",
        "sort_order": x.sort_order or 0,
    }


def _ordered(query):
    return query.order_by(
        FriendLink.category.asc(),
        FriendLink.sort_order.asc(),
        FriendLink.id.asc(),
    )


@router.get("", summary="\u516c\u5f00\uff1a\u83b7\u53d6\u5168\u90e8\u53cb\u94fe")
def list_public(db: Annotated[Session, Depends(get_db)]):
    rows = _ordered(db.query(FriendLink)).all()
    return ok({"links": [_serialize(r) for r in rows]})


@router.get("/admin/categories", summary="\u7ba1\u7406\uff1a\u83b7\u53d6\u5206\u7c7b\u5217\u8868")
def list_categories(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    rows = (
        db.query(FriendLink.category)
        .filter(FriendLink.category.isnot(None), FriendLink.category != "")
        .distinct()
        .order_by(FriendLink.category.asc())
        .all()
    )
    return ok({"categories": [r[0] for r in rows]})


@router.get("/admin", summary="\u7ba1\u7406\uff1a\u5206\u9875\u641c\u7d22\u53cb\u94fe")
def list_admin(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(""),
    category: str = Query(""),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=200),
):
    query = db.query(FriendLink)
    q = (q or "").strip()
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                FriendLink.name.like(like),
                FriendLink.url.like(like),
                FriendLink.description.like(like),
            )
        )
    category = (category or "").strip()
    if category:
        query = query.filter(FriendLink.category == category)
    total = query.count()
    rows = _ordered(query).offset((page - 1) * pageSize).limit(pageSize).all()
    return ok({"links": [_serialize(r) for r in rows], "total": total, "page": page, "pageSize": pageSize})


@router.post("/admin", status_code=201, summary="\u7ba1\u7406\uff1a\u65b0\u589e\u53cb\u94fe")
def create_link(
    body: LinkBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    name = body.name.strip()
    url = body.url.strip()
    if not name or not url:
        raise HTTPException(status_code=400, detail="\u540d\u79f0\u548c\u94fe\u63a5\u4e0d\u80fd\u4e3a\u7a7a")
    row = FriendLink(
        name=name,
        url=url,
        image_url=(body.image_url or "").strip() or None,
        description=(body.description or "").strip() or None,
        category=(body.category or "").strip() or None,
        sort_order=body.sort_order or 0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(_serialize(row))


@router.patch("/admin/{link_id}", summary="\u7ba1\u7406\uff1a\u4fee\u6539\u53cb\u94fe")
def update_link(
    link_id: int,
    body: LinkUpdateBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    row = db.query(FriendLink).filter(FriendLink.id == link_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="\u53cb\u94fe\u4e0d\u5b58\u5728")
    if body.name is not None:
        new_name = body.name.strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="\u540d\u79f0\u4e0d\u80fd\u4e3a\u7a7a")
        row.name = new_name
    if body.url is not None:
        new_url = body.url.strip()
        if not new_url:
            raise HTTPException(status_code=400, detail="\u94fe\u63a5\u4e0d\u80fd\u4e3a\u7a7a")
        row.url = new_url
    if body.image_url is not None:
        row.image_url = body.image_url.strip() or None
    if body.description is not None:
        row.description = body.description.strip() or None
    if body.category is not None:
        row.category = body.category.strip() or None
    if body.sort_order is not None:
        row.sort_order = body.sort_order
    db.commit()
    db.refresh(row)
    return ok(_serialize(row))


@router.delete("/admin/{link_id}", summary="\u7ba1\u7406\uff1a\u5220\u9664\u53cb\u94fe")
def delete_link(
    link_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    row = db.query(FriendLink).filter(FriendLink.id == link_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="\u53cb\u94fe\u4e0d\u5b58\u5728")
    db.delete(row)
    db.commit()
    return ok({"ok": True, "id": link_id})