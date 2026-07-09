from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.response import ok
from app.models.qa import QaMessage
from app.schemas.qa import QaMessageCreate, QaMessagePublic

router = APIRouter(prefix="/qa", tags=["qa"])


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


@router.post("/messages", summary="提交棉花糖留言", status_code=201)
def create_message(
    payload: QaMessageCreate,
    db: Annotated[Session, Depends(get_db)],
):
    row = QaMessage(
        name=(payload.name or "访客").strip()[:50] or "访客",
        content=payload.content.strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(QaMessagePublic.model_validate(row).model_dump(), message="已送达棉花糖")
