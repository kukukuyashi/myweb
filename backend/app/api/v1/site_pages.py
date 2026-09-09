from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.notes_admin import require_notes_admin
from app.core.db import get_db
from app.core.response import ok
from app.models.site_page_config import SitePageConfig


router = APIRouter(prefix="/site-pages", tags=["site-pages"])

ALLOWED_PAGE_KEYS = {"about", "archive"}


class SitePageBody(BaseModel):
    content: dict[str, Any] = Field(min_length=1)


def _serialize(row: SitePageConfig) -> dict:
    return {
        "page_key": row.page_key,
        "content": row.content or {},
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@router.get("/{page_key}", summary="公开：获取页面配置")
def get_page(page_key: str, db: Annotated[Session, Depends(get_db)]):
    if page_key not in ALLOWED_PAGE_KEYS:
        raise HTTPException(status_code=404, detail="页面不存在")
    row = db.query(SitePageConfig).filter(SitePageConfig.page_key == page_key).first()
    if not row:
        return ok({"page_key": page_key, "content": None, "updated_at": None})
    return ok(_serialize(row))


@router.put("/{page_key}", summary="管理：保存页面配置")
def put_page(
    page_key: str,
    body: SitePageBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    if page_key not in ALLOWED_PAGE_KEYS:
        raise HTTPException(status_code=404, detail="页面不存在")
    row = db.query(SitePageConfig).filter(SitePageConfig.page_key == page_key).first()
    if not row:
        row = SitePageConfig(page_key=page_key, content=body.content)
        db.add(row)
    else:
        row.content = body.content
    db.commit()
    db.refresh(row)
    return ok(_serialize(row))
