import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def notify_post_published(payload: dict) -> None:
    """发文后异步通知 N8N Webhook；失败只打日志，不阻塞发布。"""
    settings = get_settings()
    if not settings.n8n_webhook_url:
        return

    headers = {"Content-Type": "application/json"}
    if settings.n8n_webhook_secret:
        headers["X-Webhook-Secret"] = settings.n8n_webhook_secret

    try:
        with httpx.Client(timeout=settings.n8n_timeout_sec) as client:
            resp = client.post(settings.n8n_webhook_url, json=payload, headers=headers)
            resp.raise_for_status()
        logger.info("n8n webhook ok post_id=%s", payload.get("post_id"))
    except Exception as exc:
        logger.warning("n8n webhook failed: %s", exc)


def build_post_published_payload(post, author) -> dict:
    settings = get_settings()
    base = (settings.public_site_url or "http://127.0.0.1:5173/myweb").rstrip("/")
    published_at = post.published_at.isoformat() if post.published_at else None
    return {
        "event": "post.published",
        "post_id": post.id,
        "title": post.title,
        "slug": post.slug,
        "category": post.category,
        "tags": post.tags or [],
        "url": f"{base}/content/{post.id}",
        "author": author.username,
        "author_nickname": author.nickname,
        "published_at": published_at,
    }
