import json
from typing import Any

import redis

from app.core.config import get_settings

_client: redis.Redis | None = None
_available: bool | None = None

POST_LIST_PREFIX = "posts:list:"
POST_LIST_TTL = 300


def _get_client() -> redis.Redis | None:
    global _client, _available
    if _available is False:
        return None
    if _client is None:
        settings = get_settings()
        if not settings.redis_url:
            _available = False
            return None
        try:
            _client = redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
            _client.ping()
            _available = True
        except Exception:
            _available = False
            _client = None
            return None
    return _client


def cache_get(key: str) -> Any | None:
    client = _get_client()
    if not client:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = POST_LIST_TTL) -> None:
    client = _get_client()
    if not client:
        return
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def invalidate_post_lists() -> None:
    client = _get_client()
    if not client:
        return
    try:
        for key in client.scan_iter(f"{POST_LIST_PREFIX}*"):
            client.delete(key)
    except Exception:
        pass


def post_list_cache_key(page: int, page_size: int, category: str | None, status: str) -> str:
    cat = category or "all"
    return f"{POST_LIST_PREFIX}p{page}:s{page_size}:c{cat}:st{status}"
