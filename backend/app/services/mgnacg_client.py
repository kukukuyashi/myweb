import asyncio
import logging
import re
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

CACHE_PREFIX = "mgnacg:watch:"
CACHE_TTL = 7 * 24 * 3600
REQUEST_TIMEOUT = 6.0
USER_AGENT = "CYINC-Platform/1.0 (https://cyinc.ink)"
SUGGEST_LIMIT = 8
_RESOLVE_SEM = asyncio.Semaphore(4)

_memory_cache: dict[str, tuple[float, str | None]] = {}


def _base_url() -> str:
    return get_settings().mgnacg_base_url.rstrip("/")


def play_url(vod_id: int, base: str | None = None) -> str:
    root = (base or _base_url()).rstrip("/")
    return f"{root}/index.php?m=vod-play-id-{int(vod_id)}-sid-1-nid-1"


def _cache_key(name_cn: str | None, name: str | None) -> str:
    label = (name_cn or name or "").strip().lower()
    label = re.sub(r"\s+", "", label)
    return f"{CACHE_PREFIX}{label}"


def _memory_get(key: str) -> str | None | object:
    row = _memory_cache.get(key)
    if not row:
        return None
    expires, data = row
    if time.time() > expires:
        _memory_cache.pop(key, None)
        return None
    return data


def _memory_set(key: str, data: str | None, ttl: int) -> None:
    _memory_cache[key] = (time.time() + ttl, data)


def _cached_get(key: str) -> str | None | object:
    data = cache_get(key)
    if data is not None:
        return data
    return _memory_get(key)


def _cached_set(key: str, data: str | None, ttl: int = CACHE_TTL) -> None:
    cache_set(key, data, ttl)
    _memory_set(key, data, ttl)


def _search_query(name_cn: str | None, name: str | None) -> str:
    label = (name_cn or name or "").strip()
    label = re.sub(r"[～~].*$", "", label)
    label = re.sub(r"\s*第[一二三四五六七八九十\d]+季.*$", "", label)
    label = re.sub(r"\s*第[一二三四五六七八九十\d]+期.*$", "", label)
    return label.strip() or (name or "").strip()


def _normalize_title(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[\s:：·・\-—_（）()【】\[\]《》<>「」『』\"'，,。.!！?？]", "", text)
    return text


def _score_match(query: str, candidate_name: str) -> float:
    q = _normalize_title(query)
    c = _normalize_title(candidate_name)
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0
    if q in c or c in q:
        return 0.85
    q_set = set(q)
    c_set = set(c)
    overlap = len(q_set & c_set) / max(len(q_set), 1)
    return overlap * 0.6


async def _suggest(client: httpx.AsyncClient, query: str) -> list[dict[str, Any]]:
    if not query:
        return []
    res = await client.get(
        f"{_base_url()}/index.php/ajax/suggest",
        params={"mid": 1, "wd": query, "limit": SUGGEST_LIMIT, "timestamp": int(time.time())},
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    res.raise_for_status()
    data = res.json()
    if not isinstance(data, dict) or data.get("code") != 1:
        return []
    return data.get("list") or []


async def resolve_watch_url(
    name_cn: str | None,
    name: str | None,
    *,
    vod_id: int | None = None,
) -> str | None:
    """解析橘子动漫播放页直链。"""
    if not get_settings().mgnacg_enabled:
        return None

    if vod_id:
        return play_url(vod_id)

    query = _search_query(name_cn, name)
    if not query:
        return None

    cache_key = _cache_key(name_cn, name)
    cached = _cached_get(cache_key)
    if cached is not None:
        return cached or None

    try:
        async with _RESOLVE_SEM:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
                candidates = await _suggest(client, query)
    except Exception as exc:
        logger.warning("mgnacg suggest failed for %r: %s", query, exc)
        return None

    best_id: int | None = None
    best_score = 0.0
    for row in candidates:
        title = row.get("name") or ""
        score = _score_match(query, title)
        if score > best_score:
            best_score = score
            best_id = row.get("id")

    url: str | None = play_url(best_id) if best_id and best_score >= 0.45 else None
    _cached_set(cache_key, url)
    return url


async def attach_watch_urls(items: list[dict], *, live_suggest: bool = True) -> list[dict]:
    """为番剧列表批量附加 watch_url。"""

    async def _one(item: dict) -> dict:
        out = dict(item)
        if out.get("watch_url"):
            return out
        vod_id = out.get("mgnacg_vod_id")
        if vod_id and get_settings().mgnacg_enabled:
            out["watch_url"] = play_url(vod_id)
            return out
        if not live_suggest:
            return out
        url = await resolve_watch_url(
            out.get("name_cn"),
            out.get("name"),
            vod_id=vod_id,
        )
        if url:
            out["watch_url"] = url
        return out

    if not items:
        return items
    return await asyncio.gather(*[_one(item) for item in items])


async def enrich_schedule_watch_urls(
    season: list[dict],
    today_items: list[dict],
    weekdays: list[dict],
    *,
    live_suggest: bool = False,
) -> tuple[list[dict], list[dict], list[dict]]:
    """按 bangumi_id 去重后解析一次 watch_url，再写回各列表。"""
    by_id: dict[int, dict] = {}
    for item in season:
        bid = item.get("bangumi_id")
        if bid:
            by_id[bid] = item

    resolved = await attach_watch_urls(list(by_id.values()), live_suggest=live_suggest)
    url_by_id = {
        row["bangumi_id"]: row["watch_url"]
        for row in resolved
        if row.get("bangumi_id") and row.get("watch_url")
    }

    def merge(items: list[dict]) -> list[dict]:
        out: list[dict] = []
        for item in items:
            row = dict(item)
            url = url_by_id.get(row.get("bangumi_id"))
            if url:
                row["watch_url"] = url
            out.append(row)
        return out

    return (
        merge(season),
        merge(today_items),
        [{**day, "items": merge(day.get("items") or [])} for day in weekdays],
    )
