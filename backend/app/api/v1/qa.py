from time import monotonic
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.api.v1.notes_admin import require_notes_admin
from app.core.db import get_db
from app.core.response import ok
from app.models.qa import QaMessage
from app.models.user import User
from app.schemas.qa import QaMessageCreate, QaMessagePublic
from app.services.qa_settings import load_settings, save_settings

router = APIRouter(prefix="/qa", tags=["qa"])

# 同一 IP 最近一次提交时间（单进程内存态，重启即重置）
_last_submit_by_ip: dict[str, float] = {}


class QaSettingsBody(BaseModel):
    submit_enabled: bool | None = None
    require_login: bool | None = None
    min_interval_seconds: int | None = None
    blocked_keywords: list[str] | None = None


@router.get("/messages", summary="棉花糖 Q&A 列表")
def list_messages(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
):
    rows = (
        db.query(QaMessage)
        .order_by(QaMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    return ok([QaMessagePublic.model_validate(r).model_dump() for r in rows])


@router.get("/board-status", summary="留言板公开状态（供前端渲染提示）")
def board_status(db: Annotated[Session, Depends(get_db)]):
    settings = load_settings(db)
    return ok(
        {
            "submit_enabled": settings["submit_enabled"],
            "require_login": settings["require_login"],
        }
    )


@router.post("/messages", summary="提交棉花糖留言", status_code=201)
def create_message(
    payload: QaMessageCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
):
    settings = load_settings(db)
    if not settings["submit_enabled"]:
        raise HTTPException(status_code=403, detail="留言板暂时关闭，稍后再来看看～")
    if settings["require_login"] and current_user is None:
        raise HTTPException(status_code=401, detail="请先登录后再留言")

    content = payload.content.strip()
    haystack = f"{payload.name or ''}\n{content}".lower()
    for kw in settings["blocked_keywords"]:
        if kw.lower() in haystack:
            raise HTTPException(status_code=400, detail="留言含有不支持的内容，换个说法试试？")

    interval = settings["min_interval_seconds"]
    if interval > 0:
        ip = request.client.host if request.client else "unknown"
        now = monotonic()
        last = _last_submit_by_ip.get(ip)
        if last is not None and now - last < interval:
            wait = int(interval - (now - last)) + 1
            raise HTTPException(status_code=429, detail=f"说得太快啦，{wait} 秒后再试～")
        if len(_last_submit_by_ip) > 5000:
            _last_submit_by_ip.clear()
        _last_submit_by_ip[ip] = now

    name = (payload.name or "").strip()[:50]
    if not name:
        name = (current_user.nickname or current_user.username) if current_user else "访客"
    row = QaMessage(name=name or "访客", content=content)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(QaMessagePublic.model_validate(row).model_dump(), message="已送达棉花糖")


@router.get("/admin/settings", summary="留言板防护设置（管理端）")
def get_qa_settings(
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok({"settings": load_settings(db)})


@router.put("/admin/settings", summary="保存留言板防护设置")
def put_qa_settings(
    body: QaSettingsBody,
    _: Annotated[str, Depends(require_notes_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    merged = save_settings(db, body.model_dump(exclude_unset=True))
    return ok({"settings": merged}, message="设置已保存")
