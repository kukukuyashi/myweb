import random
import string
import time

from app.services.cache import cache_available, cache_delete, cache_get, cache_set

VERIFY_PREFIX = "email_verify:"
VERIFY_TTL = 600
RATE_PREFIX = "email_rate:"
RATE_TTL = 60

# Redis 不可用时的进程内备用存储（本地开发）
_mem: dict[str, tuple[str, float]] = {}


def _norm_email(email: str) -> str:
    return email.strip().lower()


def _mem_get(key: str) -> str | None:
    item = _mem.get(key)
    if not item:
        return None
    value, expires = item
    if time.time() > expires:
        _mem.pop(key, None)
        return None
    return value


def _mem_set(key: str, value: str, ttl: int) -> bool:
    _mem[key] = (value, time.time() + ttl)
    return True


def _mem_delete(key: str) -> None:
    _mem.pop(key, None)


def generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def can_send_code(email: str) -> bool:
    key = f"{RATE_PREFIX}{_norm_email(email)}"
    if cache_available():
        return cache_get(key) is None
    return _mem_get(key) is None


def mark_send_rate(email: str) -> None:
    key = f"{RATE_PREFIX}{_norm_email(email)}"
    if cache_available():
        cache_set(key, "1", RATE_TTL)
    else:
        _mem_set(key, "1", RATE_TTL)


def store_code(email: str, code: str) -> bool:
    key = f"{VERIFY_PREFIX}{_norm_email(email)}"
    if cache_available():
        return cache_set(key, code, VERIFY_TTL)
    return _mem_set(key, code, VERIFY_TTL)


def verify_code(email: str, code: str) -> bool:
    key = f"{VERIFY_PREFIX}{_norm_email(email)}"
    if cache_available():
        stored = cache_get(key)
        if not stored or str(stored) != str(code).strip():
            return False
        cache_delete(key)
        return True

    stored = _mem_get(key)
    if not stored or stored != str(code).strip():
        return False
    _mem_delete(key)
    return True
