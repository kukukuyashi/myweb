from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_optional_user
from app.core.config import get_settings
from app.core.db import get_db
from app.core.response import ok
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostListItem, PostPublic, PostUpdate
from app.services.cache import cache_get, cache_set, invalidate_post_lists, post_list_cache_key
from app.services.dify_client import DifyError, run_summary_workflow
from app.services.image_upload import save_uploaded_image
from app.services.n8n_client import build_post_published_payload, notify_post_published
from app.utils.slug import slugify

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/uploads/image", summary="上传文章图片")
async def upload_post_image(
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
):
    settings = get_settings()
    url = await save_uploaded_image(
        file,
        subdir="posts",
        user_id=current_user.id,
        max_bytes=settings.max_forum_image_bytes,
    )
    return ok({"url": url}, message="上传成功")


def _author_dict(user: User | None) -> dict | None:
    if not user:
        return None
    return {"id": user.id, "username": user.username, "nickname": user.nickname}


def _post_to_public(post: Post) -> dict:
    data = PostPublic.model_validate(post).model_dump()
    data["author"] = _author_dict(post.author)
    return data


def _post_to_list_item(post: Post) -> dict:
    data = PostListItem.model_validate(post).model_dump()
    data["author"] = _author_dict(post.author)
    return data


def _ensure_unique_slug(db: Session, base_slug: str, exclude_id: int | None = None) -> str:
    slug = base_slug
    n = 1
    while True:
        q = db.query(Post).filter(Post.slug == slug)
        if exclude_id:
            q = q.filter(Post.id != exclude_id)
        if not q.first():
            return slug
        n += 1
        slug = f"{base_slug}-{n}"


def _apply_publish_time(post: Post, new_status: str | None = None) -> None:
    status_val = new_status or post.status
    if status_val == "published" and post.published_at is None:
        post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("", summary="文章列表")
def list_posts(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category: str | None = None,
    status_filter: str = Query("published", alias="status"),
):
    cache_key = post_list_cache_key(page, page_size, category, status_filter)
    cached = cache_get(cache_key)
    if cached is not None:
        return ok(cached)

    q = db.query(Post).options(joinedload(Post.author))
    if status_filter:
        q = q.filter(Post.status == status_filter)
    if category:
        q = q.filter(Post.category == category)

    total = q.count()
    rows = (
        q.order_by(Post.published_at.desc(), Post.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    payload = {
        "items": [_post_to_list_item(p) for p in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    cache_set(cache_key, payload)
    return ok(payload)


@router.get("/mine", summary="我的文章（含草稿）")
def my_posts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    q = db.query(Post).options(joinedload(Post.author)).filter(Post.user_id == current_user.id)
    total = q.count()
    rows = (
        q.order_by(Post.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ok(
        {
            "items": [_post_to_list_item(p) for p in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/{post_id}", summary="文章详情")
def get_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
):
    post = db.query(Post).options(joinedload(Post.author)).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if post.status != "published":
        if not current_user or post.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return ok(_post_to_public(post))


@router.post("", summary="创建文章")
def create_post(
    payload: PostCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    base_slug = slugify(payload.slug or payload.title)
    slug = _ensure_unique_slug(db, base_slug)
    post = Post(
        user_id=current_user.id,
        title=payload.title,
        slug=slug,
        content=payload.content,
        category=payload.category,
        tags=payload.tags,
        status=payload.status,
        cover_url=payload.cover_url,
    )
    _apply_publish_time(post, payload.status)
    db.add(post)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug 已存在") from exc
    db.refresh(post)
    post = db.query(Post).options(joinedload(Post.author)).filter(Post.id == post.id).one()
    invalidate_post_lists()
    if post.status == "published":
        background_tasks.add_task(
            notify_post_published,
            build_post_published_payload(post, current_user),
        )
    return ok(_post_to_public(post), message="创建成功")


@router.post("/{post_id}/summary", summary="Dify 生成/刷新文章摘要")
async def generate_post_summary(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    post = db.query(Post).options(joinedload(Post.author)).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作")

    try:
        outputs = await run_summary_workflow(post.title, post.content, user=str(current_user.id))
    except DifyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    summary = (outputs.get("summary") or outputs.get("text") or "").strip()
    if summary:
        post.ai_summary = summary[:500]
        post.ai_summary_at = datetime.now(timezone.utc).replace(tzinfo=None)
    suggested_tags = outputs.get("suggested_tags")
    if isinstance(suggested_tags, list) and suggested_tags:
        post.tags = [str(t) for t in suggested_tags[:10]]

    db.add(post)
    db.commit()
    db.refresh(post)
    invalidate_post_lists()
    return ok(
        {
            "summary": post.ai_summary,
            "suggested_tags": post.tags,
            "ai_summary_at": post.ai_summary_at,
        },
        message="摘要已更新" if summary else "Dify 未返回摘要内容",
    )


@router.patch("/{post_id}", summary="更新文章")
def update_post(
    post_id: int,
    payload: PostUpdate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    post = db.query(Post).options(joinedload(Post.author)).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权编辑")

    old_status = post.status
    data = payload.model_dump(exclude_unset=True)
    if "slug" in data and data["slug"]:
        data["slug"] = _ensure_unique_slug(db, slugify(data["slug"]), exclude_id=post.id)
    if "title" in data and "slug" not in data:
        pass

    new_status = data.get("status")
    for key, value in data.items():
        if key == "cover_url" and value == "":
            value = None
        setattr(post, key, value)
    _apply_publish_time(post, new_status)

    db.add(post)
    db.commit()
    db.refresh(post)
    invalidate_post_lists()
    if post.status == "published" and old_status != "published":
        background_tasks.add_task(
            notify_post_published,
            build_post_published_payload(post, current_user),
        )
    return ok(_post_to_public(post), message="更新成功")


@router.delete("/{post_id}", summary="删除文章")
def delete_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除")
    db.delete(post)
    db.commit()
    invalidate_post_lists()
    return ok(message="删除成功")
