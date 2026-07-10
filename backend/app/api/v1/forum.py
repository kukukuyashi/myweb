from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.response import ok
from app.models.forum import ForumCategory, ForumReply, ForumThread
from app.models.user import User
from app.schemas.forum import (
    ForumAuthor,
    ForumCategoryPublic,
    ForumReplyCreate,
    ForumReplyPublic,
    ForumThreadCreate,
    ForumThreadDetail,
    ForumThreadListItem,
    ForumThreadListResponse,
    ForumThreadUpdate,
)

router = APIRouter(prefix="/forum", tags=["forum"])


def _author_dict(user: User | None) -> ForumAuthor | None:
    if not user:
        return None
    return ForumAuthor(id=user.id, username=user.username, nickname=user.nickname)


def _thread_to_list_item(thread: ForumThread) -> dict:
    data = ForumThreadListItem(
        id=thread.id,
        category_id=thread.category_id,
        category_name=thread.category.name if thread.category else None,
        category_slug=thread.category.slug if thread.category else None,
        title=thread.title,
        reply_count=thread.reply_count,
        view_count=thread.view_count,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        author=_author_dict(thread.user),
    ).model_dump()
    return data


@router.get("/categories", summary="板块列表")
def list_categories(db: Annotated[Session, Depends(get_db)]):
    rows = db.query(ForumCategory).order_by(ForumCategory.sort_order, ForumCategory.id).all()
    items = []
    for cat in rows:
        count = db.query(ForumThread).filter(ForumThread.category_id == cat.id).count()
        item = ForumCategoryPublic.model_validate(cat)
        items.append(item.model_copy(update={"thread_count": count}).model_dump())
    return ok(items)


@router.get("/categories/{slug}/threads", summary="板块内帖子")
def list_category_threads(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    cat = db.query(ForumCategory).filter(ForumCategory.slug == slug).first()
    if not cat:
        raise HTTPException(status_code=404, detail="板块不存在")
    q = (
        db.query(ForumThread)
        .options(joinedload(ForumThread.user), joinedload(ForumThread.category))
        .filter(ForumThread.category_id == cat.id)
    )
    total = q.count()
    rows = (
        q.order_by(ForumThread.is_pinned.desc(), ForumThread.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ok(
        ForumThreadListResponse(
            items=[ForumThreadListItem.model_validate(_thread_to_list_item(r)) for r in rows],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/threads/recent", summary="最新帖子")
def recent_threads(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(5, ge=1, le=50),
):
    rows = (
        db.query(ForumThread)
        .options(joinedload(ForumThread.user), joinedload(ForumThread.category))
        .order_by(ForumThread.created_at.desc())
        .limit(limit)
        .all()
    )
    return ok({"items": [_thread_to_list_item(r) for r in rows]})


@router.get("/threads/mine", summary="我的帖子")
def my_threads(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    q = (
        db.query(ForumThread)
        .options(joinedload(ForumThread.user), joinedload(ForumThread.category))
        .filter(ForumThread.user_id == current_user.id)
    )
    total = q.count()
    rows = (
        q.order_by(ForumThread.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ok(
        ForumThreadListResponse(
            items=[ForumThreadListItem.model_validate(_thread_to_list_item(r)) for r in rows],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/threads/{thread_id}", summary="帖子详情")
def get_thread(thread_id: int, db: Annotated[Session, Depends(get_db)]):
    thread = (
        db.query(ForumThread)
        .options(
            joinedload(ForumThread.user),
            joinedload(ForumThread.category),
            joinedload(ForumThread.replies).joinedload(ForumReply.user),
        )
        .filter(ForumThread.id == thread_id)
        .first()
    )
    if not thread:
        raise HTTPException(status_code=404, detail="帖子不存在")
    thread.view_count += 1
    db.commit()
    db.refresh(thread)

    replies = [
        ForumReplyPublic(
            id=r.id,
            thread_id=r.thread_id,
            content=r.content,
            created_at=r.created_at,
            author=_author_dict(r.user),
        )
        for r in sorted(thread.replies, key=lambda x: x.created_at)
    ]
    detail = ForumThreadDetail(
        id=thread.id,
        category_id=thread.category_id,
        category_name=thread.category.name if thread.category else None,
        category_slug=thread.category.slug if thread.category else None,
        title=thread.title,
        content=thread.content,
        reply_count=thread.reply_count,
        view_count=thread.view_count,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        author=_author_dict(thread.user),
        replies=replies,
    )
    return ok(detail.model_dump())


@router.post("/threads", summary="发帖", status_code=status.HTTP_201_CREATED)
def create_thread(
    payload: ForumThreadCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    cat = db.query(ForumCategory).filter(ForumCategory.id == payload.category_id).first()
    if not cat:
        raise HTTPException(status_code=400, detail="板块不存在")
    row = ForumThread(
        category_id=payload.category_id,
        user_id=current_user.id,
        title=payload.title.strip(),
        content=payload.content.strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok({"id": row.id}, message="发帖成功")


@router.patch("/threads/{thread_id}", summary="编辑帖子")
def update_thread(
    thread_id: int,
    payload: ForumThreadUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if thread.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权编辑")
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        cat = db.query(ForumCategory).filter(ForumCategory.id == data["category_id"]).first()
        if not cat:
            raise HTTPException(status_code=400, detail="板块不存在")
    for key, value in data.items():
        if key in ("title", "content") and isinstance(value, str):
            value = value.strip()
        setattr(thread, key, value)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    thread = (
        db.query(ForumThread)
        .options(joinedload(ForumThread.user), joinedload(ForumThread.category))
        .filter(ForumThread.id == thread.id)
        .one()
    )
    return ok(_thread_to_list_item(thread), message="更新成功")


@router.delete("/threads/{thread_id}", summary="删除帖子")
def delete_thread(
    thread_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if thread.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除")
    db.delete(thread)
    db.commit()
    return ok(message="删除成功")


@router.post("/threads/{thread_id}/replies", summary="回帖", status_code=status.HTTP_201_CREATED)
def create_reply(
    thread_id: int,
    payload: ForumReplyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if thread.is_locked:
        raise HTTPException(status_code=400, detail="帖子已锁定")
    reply = ForumReply(
        thread_id=thread_id,
        user_id=current_user.id,
        content=payload.content.strip(),
    )
    thread.reply_count += 1
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return ok(
        ForumReplyPublic(
            id=reply.id,
            thread_id=reply.thread_id,
            content=reply.content,
            created_at=reply.created_at,
            author=_author_dict(current_user),
        ).model_dump(),
        message="回复成功",
    )
