from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_optional_user
from app.core.config import get_settings
from app.core.db import get_db
from app.core.response import ok
from app.models.forum import ForumCategory, ForumReply, ForumThread
from app.models.user import User
from app.models.xp import ForumReplyLike, ForumThreadLike, ForumThreadShare
from app.services.image_upload import save_uploaded_image
from app.services.level_config import get_tier
from app.services.xp_service import apply_xp, today, xp_payload
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


@router.post("/uploads/image", summary="上传论坛图片")
async def upload_forum_image(
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
):
    settings = get_settings()
    url = await save_uploaded_image(
        file,
        subdir="forum",
        user_id=current_user.id,
        max_bytes=settings.max_forum_image_bytes,
    )
    return ok({"url": url}, message="上传成功")


def _author_dict(user: User | None) -> ForumAuthor | None:
    if not user:
        return None
    tier = get_tier(user.level)
    return ForumAuthor(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        avatar=user.avatar,
        level=user.level,
        level_title=tier.title,
    )


def _thread_to_list_item(thread: ForumThread) -> dict:
    data = ForumThreadListItem(
        id=thread.id,
        category_id=thread.category_id,
        category_name=thread.category.name if thread.category else None,
        category_slug=thread.category.slug if thread.category else None,
        title=thread.title,
        reply_count=thread.reply_count,
        view_count=thread.view_count,
        like_count=thread.like_count,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        is_featured=thread.is_featured,
        cover_url=thread.cover_url,
        featured_order=thread.featured_order,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        author=_author_dict(thread.user),
    ).model_dump()
    return data


def _thread_liked(db: Session, user_id: int | None, thread_id: int) -> bool:
    if not user_id:
        return False
    return (
        db.query(ForumThreadLike)
        .filter(ForumThreadLike.user_id == user_id, ForumThreadLike.thread_id == thread_id)
        .first()
        is not None
    )


def _reply_liked_ids(db: Session, user_id: int | None, reply_ids: list[int]) -> set[int]:
    if not user_id or not reply_ids:
        return set()
    rows = (
        db.query(ForumReplyLike.reply_id)
        .filter(ForumReplyLike.user_id == user_id, ForumReplyLike.reply_id.in_(reply_ids))
        .all()
    )
    return {r[0] for r in rows}


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


@router.get("/threads/featured", summary="精选话题（贴纸墙）")
def featured_threads(db: Annotated[Session, Depends(get_db)]):
    rows = (
        db.query(ForumThread)
        .options(joinedload(ForumThread.user), joinedload(ForumThread.category))
        .filter(ForumThread.is_featured.is_(True))
        .order_by(ForumThread.featured_order.asc(), ForumThread.created_at.desc())
        .limit(7)
        .all()
    )
    items = []
    for r in rows:
        item = _thread_to_list_item(r)
        item["excerpt"] = r.title
        items.append(item)
    return ok({"items": items})


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
def get_thread(
    thread_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
):
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

    uid = current_user.id if current_user else None
    liked_reply_ids = _reply_liked_ids(db, uid, [r.id for r in thread.replies])
    replies = [
        ForumReplyPublic(
            id=r.id,
            thread_id=r.thread_id,
            content=r.content,
            like_count=r.like_count,
            liked_by_me=r.id in liked_reply_ids,
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
        cover_url=thread.cover_url,
        reply_count=thread.reply_count,
        view_count=thread.view_count,
        like_count=thread.like_count,
        share_count=thread.share_count,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        author=_author_dict(thread.user),
        replies=replies,
        liked_by_me=_thread_liked(db, uid, thread.id),
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
        cover_url=payload.cover_url,
    )
    db.add(row)
    db.flush()
    xp_result = apply_xp(db, current_user, "thread_create", ref_type="thread", ref_id=row.id)
    db.commit()
    db.refresh(row)
    xp = xp_payload(xp_result)
    msg = xp["message"] if xp else "发帖成功"
    return ok({"id": row.id, "xp": xp}, message=msg)


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
        if key == "cover_url" and value == "":
            value = None
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
    db.flush()
    xp_result = apply_xp(db, current_user, "reply_create", ref_type="reply", ref_id=reply.id)
    db.commit()
    db.refresh(reply)
    xp = xp_payload(xp_result)
    msg = xp["message"] if xp else "回复成功"
    return ok(
        ForumReplyPublic(
            id=reply.id,
            thread_id=reply.thread_id,
            content=reply.content,
            like_count=reply.like_count,
            created_at=reply.created_at,
            author=_author_dict(current_user),
        ).model_dump(),
        message=msg,
    )


@router.post("/threads/{thread_id}/like", summary="点赞帖子")
def like_thread(
    thread_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    thread = db.query(ForumThread).options(joinedload(ForumThread.user)).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="帖子不存在")
    exists = (
        db.query(ForumThreadLike)
        .filter(ForumThreadLike.user_id == current_user.id, ForumThreadLike.thread_id == thread_id)
        .first()
    )
    if exists:
        return ok({"like_count": thread.like_count, "liked": True}, message="已点赞")

    db.add(ForumThreadLike(user_id=current_user.id, thread_id=thread_id))
    thread.like_count += 1
    db.add(thread)

    xp_msgs: list[str] = []
    if thread.user_id != current_user.id:
        g = apply_xp(db, current_user, "thread_like_given", ref_type="thread", ref_id=thread_id)
        if p := xp_payload(g):
            xp_msgs.append(p["message"])
        author = db.query(User).filter(User.id == thread.user_id).first()
        if author:
            r = apply_xp(db, author, "thread_like_received", ref_type="thread", ref_id=thread_id)
            if p := xp_payload(r):
                xp_msgs.append(f"作者 {p['message']}")

    db.commit()
    db.refresh(thread)
    msg = xp_msgs[0] if xp_msgs else "点赞成功"
    return ok({"like_count": thread.like_count, "liked": True, "xp_message": msg}, message=msg)


@router.post("/replies/{reply_id}/like", summary="点赞评论")
def like_reply(
    reply_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    reply = db.query(ForumReply).options(joinedload(ForumReply.user)).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="回复不存在")
    exists = (
        db.query(ForumReplyLike)
        .filter(ForumReplyLike.user_id == current_user.id, ForumReplyLike.reply_id == reply_id)
        .first()
    )
    if exists:
        return ok({"like_count": reply.like_count, "liked": True}, message="已点赞")

    db.add(ForumReplyLike(user_id=current_user.id, reply_id=reply_id))
    reply.like_count += 1
    db.add(reply)

    msg = "点赞成功"
    if reply.user_id != current_user.id:
        g = apply_xp(db, current_user, "reply_like_given", ref_type="reply", ref_id=reply_id)
        if p := xp_payload(g):
            msg = p["message"]
        author = db.query(User).filter(User.id == reply.user_id).first()
        if author:
            apply_xp(db, author, "reply_like_received", ref_type="reply", ref_id=reply_id)

    db.commit()
    db.refresh(reply)
    return ok({"like_count": reply.like_count, "liked": True}, message=msg)


@router.post("/threads/{thread_id}/share", summary="分享帖子")
def share_thread(
    thread_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="帖子不存在")

    share_day = today()
    exists = (
        db.query(ForumThreadShare)
        .filter(
            ForumThreadShare.user_id == current_user.id,
            ForumThreadShare.thread_id == thread_id,
            ForumThreadShare.share_date == share_day,
        )
        .first()
    )
    if exists:
        return ok({"share_count": thread.share_count}, message="今日已分享过该帖")

    db.add(ForumThreadShare(user_id=current_user.id, thread_id=thread_id, share_date=share_day))
    thread.share_count += 1
    db.add(thread)
    xp_result = apply_xp(db, current_user, "thread_share", ref_type="thread", ref_id=thread_id)
    db.commit()
    db.refresh(thread)
    xp = xp_payload(xp_result)
    msg = xp["message"] if xp else "分享成功"
    return ok({"share_count": thread.share_count, "xp": xp}, message=msg)
