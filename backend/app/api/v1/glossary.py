from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.notes_admin import require_notes_admin
from app.core.db import get_db
from app.core.response import ok
from app.models.glossary import GlossaryTerm

router = APIRouter(prefix="/glossary", tags=["glossary"])


class TermBody(BaseModel):
    term: str = Field(min_length=1, max_length=128)
    definition: str = Field(min_length=1)
    aliases: str | None = None
    category: str | None = None


class TermUpdateBody(BaseModel):
    term: str | None = Field(default=None, max_length=128)
    definition: str | None = None
    aliases: str | None = None
    category: str | None = None


def _serialize(t: GlossaryTerm) -> dict:
    return {
        "id": t.id,
        "term": t.term,
        "aliases": t.aliases or "",
        "definition": t.definition,
        "category": t.category or "",
    }


@router.get("", summary="\u516c\u5f00\uff1a\u83b7\u53d6\u5168\u90e8\u672f\u8bed\uff08\u6b63\u6587\u60ac\u505c\u7528\uff09")
def list_public(db: Annotated[Session, Depends(get_db)]):
    rows = db.query(GlossaryTerm).order_by(GlossaryTerm.term.asc()).all()
    return ok({"terms": [_serialize(r) for r in rows]})


@router.get("/admin/categories", summary="\u7ba1\u7406\uff1a\u83b7\u53d6\u5206\u7c7b\u5217\u8868")
def list_categories(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    rows = (
        db.query(GlossaryTerm.category)
        .filter(GlossaryTerm.category.isnot(None), GlossaryTerm.category != "")
        .distinct()
        .order_by(GlossaryTerm.category.asc())
        .all()
    )
    return ok({"categories": [r[0] for r in rows]})


@router.get("/admin", summary="\u7ba1\u7406\uff1a\u5206\u9875\u641c\u7d22\u672f\u8bed")
def list_admin(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(""),
    category: str = Query(""),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=200),
):
    query = db.query(GlossaryTerm)
    q = (q or "").strip()
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                GlossaryTerm.term.like(like),
                GlossaryTerm.aliases.like(like),
                GlossaryTerm.definition.like(like),
            )
        )
    category = (category or "").strip()
    if category:
        query = query.filter(GlossaryTerm.category == category)
    total = query.count()
    rows = (
        query.order_by(GlossaryTerm.term.asc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )
    return ok({"terms": [_serialize(r) for r in rows], "total": total, "page": page, "pageSize": pageSize})


@router.post("/admin", status_code=201, summary="\u7ba1\u7406\uff1a\u65b0\u589e\u672f\u8bed")
def create_term(
    body: TermBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    term = body.term.strip()
    if not term:
        raise HTTPException(status_code=400, detail="\u672f\u8bed\u540d\u4e0d\u80fd\u4e3a\u7a7a")
    exists = db.query(GlossaryTerm).filter(GlossaryTerm.term == term).first()
    if exists:
        raise HTTPException(status_code=409, detail=f"\u672f\u8bed\u5df2\u5b58\u5728\uff1a{term}")
    row = GlossaryTerm(
        term=term,
        definition=body.definition.strip(),
        aliases=(body.aliases or "").strip() or None,
        category=(body.category or "").strip() or None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(_serialize(row))


@router.patch("/admin/{term_id}", summary="\u7ba1\u7406\uff1a\u4fee\u6539\u672f\u8bed")
def update_term(
    term_id: int,
    body: TermUpdateBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    row = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="\u672f\u8bed\u4e0d\u5b58\u5728")
    if body.term is not None:
        new_term = body.term.strip()
        if not new_term:
            raise HTTPException(status_code=400, detail="\u672f\u8bed\u540d\u4e0d\u80fd\u4e3a\u7a7a")
        clash = (
            db.query(GlossaryTerm)
            .filter(GlossaryTerm.term == new_term, GlossaryTerm.id != term_id)
            .first()
        )
        if clash:
            raise HTTPException(status_code=409, detail=f"\u672f\u8bed\u5df2\u5b58\u5728\uff1a{new_term}")
        row.term = new_term
    if body.definition is not None:
        row.definition = body.definition.strip()
    if body.aliases is not None:
        row.aliases = body.aliases.strip() or None
    if body.category is not None:
        row.category = body.category.strip() or None
    db.commit()
    db.refresh(row)
    return ok(_serialize(row))


@router.delete("/admin/{term_id}", summary="\u7ba1\u7406\uff1a\u5220\u9664\u672f\u8bed")
def delete_term(
    term_id: int,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    row = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="\u672f\u8bed\u4e0d\u5b58\u5728")
    db.delete(row)
    db.commit()
    return ok({"ok": True, "id": term_id})
