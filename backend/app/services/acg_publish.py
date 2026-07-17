"""ACG 机器人发布服务：把审核通过的投稿以机器人账号写入论坛。"""

from __future__ import annotations

import secrets

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.acg import AcgSubmission
from app.models.forum import ForumCategory, ForumThread
from app.models.user import User

BOT_NICKNAME = "ACG 资讯姬"


def get_or_create_bot_user(db: Session) -> User:
    """按配置的用户名找/建机器人账号（随机密码，不可正常登录）。"""
    settings = get_settings()
    username = settings.acg_bot_username or "acg-bot"
    bot = db.query(User).filter(User.username == username).first()
    if bot:
        return bot

    bot = User(
        username=username,
        email=f"{username}@bot.cyinc.ink",
        password_hash=get_password_hash(secrets.token_urlsafe(24)),
        nickname=BOT_NICKNAME,
    )
    db.add(bot)
    db.flush()
    return bot


def _resolve_category(db: Session, category_id: int | None) -> ForumCategory:
    if category_id:
        cat = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
        if cat:
            return cat

    settings = get_settings()
    slug = (settings.acg_bot_category_slug or "").strip()
    if slug:
        cat = db.query(ForumCategory).filter(ForumCategory.slug == slug).first()
        if cat:
            return cat

    cat = db.query(ForumCategory).order_by(ForumCategory.sort_order, ForumCategory.id).first()
    if not cat:
        raise ValueError("论坛暂无板块，无法发布")
    return cat


def publish_submission(db: Session, submission: AcgSubmission) -> ForumThread:
    """把投稿发布为论坛帖子；回填 published_thread_id 与 status。"""
    if submission.status == "published":
        raise ValueError("该投稿已发布")
    if submission.status == "discarded":
        raise ValueError("该投稿已被丢弃，无法发布")

    title = (submission.title or "").strip()
    content = (submission.content or "").strip()
    if not title or not content:
        raise ValueError("标题或正文为空，无法发布")

    bot = get_or_create_bot_user(db)
    category = _resolve_category(db, submission.category_id)

    thread = ForumThread(
        category_id=category.id,
        user_id=bot.id,
        title=title,
        content=content,
        cover_url=submission.cover_url,
    )
    db.add(thread)
    db.flush()

    submission.status = "published"
    submission.published_thread_id = thread.id
    submission.category_id = category.id
    db.commit()
    db.refresh(thread)
    return thread
