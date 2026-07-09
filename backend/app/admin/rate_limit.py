import time
from collections import defaultdict

MAX_ATTEMPTS = 5
WINDOW_SEC = 900  # 15 分钟内最多 5 次失败

_failures: dict[str, list[float]] = defaultdict(list)


def client_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def is_locked(ip: str) -> bool:
    now = time.time()
    recent = [t for t in _failures[ip] if now - t < WINDOW_SEC]
    _failures[ip] = recent
    return len(recent) >= MAX_ATTEMPTS


def record_failure(ip: str) -> None:
    _failures[ip].append(time.time())


def clear_failures(ip: str) -> None:
    _failures.pop(ip, None)


def lockout_seconds_remaining(ip: str) -> int:
    if not _failures[ip]:
        return 0
    oldest = min(_failures[ip])
    return max(0, int(WINDOW_SEC - (time.time() - oldest)))
