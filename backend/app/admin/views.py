import json
import re
from typing import Any

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import TextAreaField

from app.admin.labels import (
    FORUM_CATEGORY_LABELS,
    FORUM_REPLY_LABELS,
    FORUM_THREAD_LABELS,
    POST_LABELS,
    QA_LABELS,
    USER_LABELS,
)
from app.core.db import SessionLocal
from app.models.forum import ForumCategory, ForumReply, ForumThread
from app.models.post import Post
from app.models.qa import QaMessage
from app.models.user import User
from app.utils.slug import slugify

_CONTENT_WIDGET = {"rows": 16, "style": "font-family: ui-monospace, SFMono-Regular, Menlo, monospace;"}


def _parse_tags(value: Any) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except json.JSONDecodeError:
                pass
        return [t.strip() for t in re.split(r"[,，、]", text) if t.strip()]
    return []


def _unique_post_slug(base: str, exclude_id: int | None = None) -> str:
    base = slugify(base) if base else slugify("post")
    db = SessionLocal()
    try:
        candidate = base
        n = 2
        while True:
            q = db.query(Post).filter(Post.slug == candidate)
            if exclude_id is not None:
                q = q.filter(Post.id != exclude_id)
            if q.first() is None:
                return candidate
            candidate = f"{base}-{n}"
            n += 1
    finally:
        db.close()


class UserAdmin(ModelView, model=User):
    identity = "user"
    name = "用户"
    name_plural = "用户"
    icon = "fa-solid fa-user"
    column_labels = USER_LABELS

    column_list = [
        User.id,
        User.username,
        User.email,
        User.nickname,
        User.level,
        User.xp,
        User.checkin_streak,
        User.created_at,
    ]
    column_searchable_list = [User.username, User.email, User.nickname]
    column_sortable_list = [User.id, User.username, User.created_at]
    column_details_exclude_list = [User.password_hash]
    form_excluded_columns = [User.password_hash, User.created_at, User.updated_at]

    can_create = False
    can_delete = True
    can_edit = True
    can_view_details = True


class PostAdmin(ModelView, model=Post):
    identity = "post"
    """博客 API 文章（与静态 Content/*.html 不同，供主站 / 发文 API 使用）。"""

    name = "文章"
    name_plural = "文章"
    icon = "fa-solid fa-file-lines"
    column_labels = POST_LABELS

    column_list = [
        Post.id,
        Post.title,
        Post.category,
        Post.status,
        Post.author,
        Post.published_at,
        Post.created_at,
    ]
    column_searchable_list = [Post.title, Post.slug, Post.category]
    column_sortable_list = [Post.id, Post.title, Post.published_at, Post.created_at]
    column_default_sort = [(Post.created_at, True)]

    # 用 relationship 下拉选择作者，避免手填 user_id
    form_columns = [
        Post.author,
        Post.title,
        Post.slug,
        Post.content,
        Post.category,
        Post.tags,
        Post.status,
        Post.cover_url,
        Post.ai_summary,
        Post.published_at,
    ]
    form_args = {
        "slug": {
            "description": "链接别名，可留空；保存时按标题自动生成，并保证唯一",
        },
        "content": {
            "description": "支持 Markdown 正文",
        },
        "tags": {
            "description": '标签：填 JSON 如 ["前端","Vue"]，或逗号分隔：前端,Vue',
        },
        "status": {
            "description": "draft=草稿，published=已发布",
        },
        "cover_url": {
            "description": "封面图路径，如 /myweb/img/xxx.jpg 或完整 URL",
        },
        "category": {
            "description": "分类文本，如：前端 / 部署 / 项目",
        },
        "published_at": {
            "description": "发布为 published 时可填发布时间；留空则前台按创建时间处理",
        },
    }
    form_widget_args = {
        "content": _CONTENT_WIDGET,
        "ai_summary": {"rows": 3},
        "tags": {"rows": 2},
        "cover_url": {"rows": 1},
    }
    form_overrides = {
        "content": TextAreaField,
        "ai_summary": TextAreaField,
        "tags": TextAreaField,
        "cover_url": TextAreaField,
    }

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True

    async def on_model_change(
        self,
        data: dict,
        model: Any,
        is_created: bool,
        request: Request,
    ) -> None:
        data["tags"] = _parse_tags(data.get("tags"))
        if not (data.get("category") or "").strip():
            data["category"] = "未分类"
        if not (data.get("status") or "").strip():
            data["status"] = "draft"

        title = (data.get("title") or getattr(model, "title", "") or "").strip()
        slug = (data.get("slug") or "").strip() if data.get("slug") is not None else ""
        if not slug:
            slug = title
        data["slug"] = _unique_post_slug(slug, exclude_id=None if is_created else getattr(model, "id", None))


class ForumCategoryAdmin(ModelView, model=ForumCategory):
    identity = "forum-category"
    name = "论坛板块"
    name_plural = "论坛板块"
    icon = "fa-solid fa-folder"
    column_labels = FORUM_CATEGORY_LABELS

    column_list = [ForumCategory.id, ForumCategory.name, ForumCategory.slug, ForumCategory.sort_order]
    column_searchable_list = [ForumCategory.name, ForumCategory.slug]
    column_sortable_list = [ForumCategory.id, ForumCategory.sort_order]
    form_columns = [
        ForumCategory.name,
        ForumCategory.slug,
        ForumCategory.description,
        ForumCategory.sort_order,
    ]
    form_args = {
        "slug": {"description": "英文别名，如 tech / projects / chat；可留空，保存时按名称生成"},
        "description": {"description": "板块简介，显示在前台板块卡片"},
    }
    form_overrides = {"description": TextAreaField}
    form_widget_args = {"description": {"rows": 3}}

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True

    async def on_model_change(
        self,
        data: dict,
        model: Any,
        is_created: bool,
        request: Request,
    ) -> None:
        name = (data.get("name") or getattr(model, "name", "") or "").strip()
        slug = (data.get("slug") or "").strip() if data.get("slug") is not None else ""
        if not slug:
            slug = slugify(name) if name else slugify("category")
        data["slug"] = slug
        if data.get("sort_order") in (None, ""):
            data["sort_order"] = 0


class ForumThreadAdmin(ModelView, model=ForumThread):
    identity = "forum-thread"
    name = "论坛帖子"
    name_plural = "论坛帖子"
    icon = "fa-solid fa-comments"
    column_labels = FORUM_THREAD_LABELS

    column_list = [
        ForumThread.id,
        ForumThread.title,
        ForumThread.category,
        ForumThread.user,
        ForumThread.is_featured,
        ForumThread.featured_order,
        ForumThread.reply_count,
        ForumThread.view_count,
        ForumThread.is_pinned,
        ForumThread.is_locked,
        ForumThread.created_at,
    ]
    column_searchable_list = [ForumThread.title, ForumThread.content]
    column_sortable_list = [
        ForumThread.id,
        ForumThread.created_at,
        ForumThread.reply_count,
        ForumThread.featured_order,
    ]
    column_default_sort = [(ForumThread.created_at, True)]

    form_columns = [
        ForumThread.category,
        ForumThread.user,
        ForumThread.title,
        ForumThread.content,
        ForumThread.is_featured,
        ForumThread.cover_url,
        ForumThread.featured_order,
        ForumThread.is_pinned,
        ForumThread.is_locked,
    ]
    form_args = {
        "category": {"description": "选择板块（没有板块时请先在「论坛板块」里新建）"},
        "user": {"description": "发帖作者（从已注册用户里选）"},
        "content": {"description": "帖子正文，支持 Markdown"},
        "cover_url": {
            "description": "精选封面，如 /myweb/img/BA/xxx.jpg（精选到主站贴纸墙时建议填写）",
        },
        "featured_order": {"description": "精选排序，越小越靠前；非精选可留空"},
        "is_featured": {"description": "勾选后出现在主站精选/贴纸墙"},
        "is_pinned": {"description": "板块内置顶"},
        "is_locked": {"description": "锁定后前台不可再回帖"},
    }
    form_overrides = {"content": TextAreaField, "cover_url": TextAreaField}
    form_widget_args = {
        "content": _CONTENT_WIDGET,
        "cover_url": {"rows": 1},
    }

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True

    async def on_model_change(
        self,
        data: dict,
        model: Any,
        is_created: bool,
        request: Request,
    ) -> None:
        if is_created:
            data.setdefault("reply_count", 0)
            data.setdefault("view_count", 0)
            data.setdefault("like_count", 0)
            data.setdefault("share_count", 0)
            data.setdefault("is_pinned", False)
            data.setdefault("is_locked", False)
            data.setdefault("is_featured", False)


class ForumReplyAdmin(ModelView, model=ForumReply):
    identity = "forum-reply"
    name = "论坛回复"
    name_plural = "论坛回复"
    icon = "fa-solid fa-reply"
    column_labels = FORUM_REPLY_LABELS

    column_list = [
        ForumReply.id,
        ForumReply.thread,
        ForumReply.user,
        ForumReply.content,
        ForumReply.created_at,
    ]
    column_searchable_list = [ForumReply.content]
    column_sortable_list = [ForumReply.id, ForumReply.created_at]
    column_default_sort = [(ForumReply.created_at, True)]
    form_columns = [ForumReply.thread, ForumReply.user, ForumReply.content]
    form_args = {
        "thread": {"description": "回复到哪条帖子"},
        "user": {"description": "回复作者"},
        "content": {"description": "回复正文"},
    }
    form_overrides = {"content": TextAreaField}
    form_widget_args = {"content": {"rows": 8}}

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True

    async def after_model_change(
        self,
        data: dict,
        model: Any,
        is_created: bool,
        request: Request,
    ) -> None:
        if not is_created or not model.thread_id:
            return
        db = SessionLocal()
        try:
            thread = db.get(ForumThread, model.thread_id)
            if thread is None:
                return
            thread.reply_count = (
                db.query(ForumReply).filter(ForumReply.thread_id == thread.id).count()
            )
            db.add(thread)
            db.commit()
        finally:
            db.close()


class QaMessageAdmin(ModelView, model=QaMessage):
    identity = "qa-message"
    name = "留言板"
    name_plural = "留言板"
    icon = "fa-solid fa-message"
    column_labels = QA_LABELS

    column_list = [QaMessage.id, QaMessage.name, QaMessage.content, QaMessage.created_at]
    column_searchable_list = [QaMessage.name, QaMessage.content]
    column_sortable_list = [QaMessage.id, QaMessage.created_at]
    column_default_sort = [(QaMessage.created_at, True)]
    form_columns = [QaMessage.name, QaMessage.content]
    form_overrides = {"content": TextAreaField}
    form_widget_args = {"content": {"rows": 6}}

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True
