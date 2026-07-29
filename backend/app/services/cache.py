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


def cache_available() -> bool:
    return _get_client() is not None


def cache_get(key: str) -> Any | None:
    client = _get_client()
    if not client:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = POST_LIST_TTL) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        if isinstance(value, str):
            client.setex(key, ttl, value)
        else:
            client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False


def cache_delete(key: str) -> None:
    client = _get_client()
    if not client:
        return
    try:
        client.delete(key)
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

def cache_incr(key: str, ttl: int) -> int | None:
    """原子自增计数器；首次自增时设置过期时间。Redis 不可用时返回 None。"""
    client = _get_client()
    if not client:
        return None
    try:
        value = client.incr(key)
        if value == 1:
            client.expire(key, ttl)
        return int(value)
    except Exception:
        return None

