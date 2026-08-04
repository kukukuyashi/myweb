"""基于 Redis 的滑动窗口速率限制，Redis 不可用时降级为内存计数（进程内，不跨 worker）。

使用方式：
    from app.utils.rate_limit import rate_limit

    @router.post("/login")
    def login(request: Request, ...):
        rate_limit(request, scope="login", max_requests=5, window_sec=900)
        ...
"""

from __future__ import annotations

import time
import threading
from collections import defaultdict

from fastapi import HTTPException, Request

from app.services.cache import cache_available, cache_incr

# ── 内存降级（进程内） ──────────────────────────────────────────
_mem_lock = threading.Lock()
_mem_buckets: dict[str, list[float]] = defaultdict(list)
_mem_window: dict[str, int] = {}  # key -> window_sec


def _mem_check(key: str, max_requests: int, window_sec: int) -> None:
    now = time.monotonic()
    with _mem_lock:
        _mem_window[key] = window_sec
        bucket = _mem_buckets[key]
        # 清理过期条目
        cutoff = now - window_sec
        while bucket and bucket[0] < cutoff:
            bucket.pop(0)
        if len(bucket) >= max_requests:
            raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
        bucket.append(now)


def rate_limit(
    request: Request,
    *,
    scope: str,
    max_requests: int,
    window_sec: int,
) -> None:
    """按客户端 IP + scope 限流。优先 Redis，不可用时降级内存。"""
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{scope}:{client_ip}"

    if cache_available():
        count = cache_incr(key, window_sec)
        if count is not None and count > max_requests:
            raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
        return

    _mem_check(key, max_requests, window_sec)