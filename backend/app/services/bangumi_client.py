import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from app.services.cache import cache_get, cache_set
from app.services.mgnacg_client import enrich_schedule_watch_urls
from app.services.cover_cache import localize_schedule_covers

logger = logging.getLogger(__name__)

BANGUMI_BASE = "https://api.bgm.tv"
CACHE_KEY_CALENDAR = "bangumi:calendar"
CACHE_KEY_SCHEDULE = "anime:schedule"
CACHE_TTL = 6 * 3600
CACHE_TTL_SCHEDULE = 6 * 3600
REQUEST_TIMEOUT = 8.0
USER_AGENT = "CYINC-Platform/1.0 (https://cyinc.ink)"
WEEKDAY_CN = {1: "星期一", 2: "星期二", 3: "星期三", 4: "星期四", 5: "星期五", 6: "星期六", 7: "星期日"}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_memory_cache: dict[str, tuple[float, Any]] = {}


class BangumiFetchError(Exception):
    pass


def _memory_get(key: str) -> Any | None:
    row = _memory_cache.get(key)
    if not row:
        return None
    expires, data = row
    if time.time() > expires:
        _memory_cache.pop(key, None)
        return None
    return data


def _memory_set(key: str, data: Any, ttl: int) -> None:
    _memory_cache[key] = (time.time() + ttl, data)


def _cached_get(key: str) -> Any | None:
    data = cache_get(key)
    if data is not None:
        return data
    return _memory_get(key)


def _cached_set(key: str, data: Any, ttl: int = CACHE_TTL) -> None:
    cache_set(key, data, ttl)
    _memory_set(key, data, ttl)


def current_season_info(now: datetime | None = None) -> dict:
    """Bangumi 季度：1/4/7/10 月为新番季。"""
    now = now or datetime.now(ZoneInfo("Asia/Shanghai"))
    y, m = now.year, now.month
    if m <= 3:
        season_month = 1
    elif m <= 6:
        season_month = 4
    elif m <= 9:
        season_month = 7
    else:
        season_month = 10
    month_label = {1: "1月", 4: "4月", 7: "7月", 10: "10月"}[season_month]
    return {
        "code": f"{y}{season_month:02d}",
        "year": y,
        "month": season_month,
        "label": f"{y}年{month_label}新番",
    }


def _load_season_fallback(season_code: str) -> dict:
    path = DATA_DIR / f"bangumi_season_fallback_{season_code}.json"
    if not path.is_file():
        raise BangumiFetchError(f"无 {season_code} 季度离线数据")
    return json.loads(path.read_text(encoding="utf-8"))


def _weekday_from_air_date(air_date: str | None) -> int | None:
    if not air_date or len(air_date) < 10:
        return None
    try:
        return datetime.fromisoformat(air_date[:10]).isoweekday()
    except ValueError:
        return None


def _calendar_weekday_map(calendar: list[dict]) -> dict[int, int]:
    out: dict[int, int] = {}
    for day in calendar:
        wid = (day.get("weekday") or {}).get("id") or 0
        for item in day.get("items") or []:
            bid = item.get("id")
            if bid:
                out[bid] = wid
    return out


def _items_to_calendar_days(items: list[dict]) -> list[dict]:
    buckets: dict[int, list[dict]] = {i: [] for i in range(1, 8)}
    for raw in items:
        wid = raw.get("air_weekday") or _weekday_from_air_date(raw.get("air_date"))
        if not wid:
            continue
        buckets.setdefault(wid, []).append(raw)
    days: list[dict] = []
    for wid in range(1, 8):
        days.append({
            "weekday": {"id": wid, "cn": WEEKDAY_CN[wid], "en": "", "ja": ""},
            "items": buckets.get(wid, []),
        })
    return days


def _cover_or_fallback(images: dict, subject_id) -> str:
    cover = images.get("large") or images.get("common") or images.get("medium") or images.get("small") or ""
    return cover


def normalize_calendar_item(item: dict, weekday_id: int) -> dict:
    images = item.get("images") or {}
    cover = _cover_or_fallback(images, item.get("id"))
    name_cn = item.get("name_cn") or item.get("name") or ""
    out = {
        "bangumi_id": item.get("id"),
        "name": item.get("name") or "",
        "name_cn": name_cn,
        "cover_url": cover,
        "air_weekday": weekday_id,
        "air_date": item.get("air_date"),
        "rating": (item.get("rating") or {}).get("score") if isinstance(item.get("rating"), dict) else item.get("score"),
        "rank": item.get("rank"),
    }
    if item.get("mgnacg_vod_id"):
        out["mgnacg_vod_id"] = item["mgnacg_vod_id"]
    return out


def normalize_subject_item(item: dict, weekday_map: dict[int, int] | None = None) -> dict:
    images = item.get("images") or {}
    bid = item.get("id")
    cover = _cover_or_fallback(images, bid)
    air_date = item.get("date") or item.get("air_date")
    weekday = (weekday_map or {}).get(bid) or item.get("air_weekday") or _weekday_from_air_date(air_date)
    name_cn = item.get("name_cn") or item.get("name") or ""
    out = {
        "bangumi_id": bid,
        "name": item.get("name") or "",
        "name_cn": name_cn,
        "cover_url": cover,
        "air_weekday": weekday,
        "air_date": air_date,
        "rating": item.get("score"),
        "rank": item.get("rank"),
    }
    if item.get("mgnacg_vod_id"):
        out["mgnacg_vod_id"] = item["mgnacg_vod_id"]
    return out


def flatten_season_items(calendar: list[dict]) -> list[dict]:
    seen: set[int] = set()
    out: list[dict] = []
    for day in calendar:
        wid = (day.get("weekday") or {}).get("id") or 0
        for item in day.get("items") or []:
            bid = item.get("id")
            if not bid or bid in seen:
                continue
            seen.add(bid)
            out.append(normalize_calendar_item(item, wid))
    return out


def items_for_weekday(calendar: list[dict], weekday_id: int) -> list[dict]:
    for day in calendar:
        if (day.get("weekday") or {}).get("id") == weekday_id:
            return [normalize_calendar_item(i, weekday_id) for i in day.get("items") or []]
    return []


def today_weekday_id() -> int:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoweekday()


def calendar_meta(calendar: list[dict], extra: dict | None = None) -> dict:
    today_id = today_weekday_id()
    weekday_cn = WEEKDAY_CN.get(today_id, "")
    for day in calendar:
        if (day.get("weekday") or {}).get("id") == today_id:
            weekday_cn = (day.get("weekday") or {}).get("cn") or weekday_cn
            break
    season = current_season_info()
    meta = {
        "today_weekday_id": today_id,
        "today_weekday_cn": weekday_cn,
        "updated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "season_code": season["code"],
        "season_label": season["label"],
    }
    if extra:
        meta.update(extra)
    return meta


async def _http_get_json(client: httpx.AsyncClient, url: str, *, params: dict | None = None) -> Any:
    res = await client.get(
        url,
        params=params,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    res.raise_for_status()
    return res.json()


async def fetch_calendar() -> tuple[list[dict], dict]:
    """周放送表：Bangumi /calendar。"""
    cached = _cached_get(CACHE_KEY_CALENDAR)
    if cached is not None:
        if isinstance(cached, dict) and "days" in cached:
            meta = {**cached.get("meta", {}), "source": "cache"}
            return cached["days"], meta
        return cached, {"source": "cache"}

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            data = await _http_get_json(client, f"{BANGUMI_BASE}/calendar")
        payload = {"days": data, "meta": {"source": "live"}}
        _cached_set(CACHE_KEY_CALENDAR, payload)
        return data, {"source": "live"}
    except Exception as exc:
        logger.warning("Bangumi calendar fetch failed: %s", exc)
        raise BangumiFetchError("Bangumi 周放送表获取失败") from exc


async def fetch_season_subjects(year: int, month: int) -> tuple[list[dict], dict]:
    """本季新番：Bangumi /v0/subjects?type=2&year=&month=。"""
    cache_key = f"bangumi:season:{year}{month:02d}"
    cached = _cached_get(cache_key)
    if cached is not None:
        if isinstance(cached, dict) and "items" in cached:
            return cached["items"], {**cached.get("meta", {}), "source": "cache"}
        return cached, {"source": "cache"}

    try:
        items: list[dict] = []
        offset = 0
        limit = 50
        total = None
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            while offset < 300:
                page = await _http_get_json(
                    client,
                    f"{BANGUMI_BASE}/v0/subjects",
                    params={"type": 2, "year": year, "month": month, "sort": "date", "limit": limit, "offset": offset},
                )
                batch = page.get("data") or []
                items.extend(batch)
                total = page.get("total", len(items))
                if not batch or len(items) >= total:
                    break
                offset += limit
        payload = {"items": items, "meta": {"source": "live", "total": total or len(items)}}
        _cached_set(cache_key, payload)
        return items, {"source": "live", "total": total or len(items)}
    except Exception as exc:
        logger.warning("Bangumi season fetch failed: %s", exc)
        raise BangumiFetchError("Bangumi 本季番剧获取失败") from exc


async def build_schedule() -> dict:
    """组装追番表：本季新番 + 周放送表 + 今日更新。"""
    cached = _cached_get(CACHE_KEY_SCHEDULE)
    if cached is not None:
        return cached

    season_info = current_season_info()
    cal_meta: dict = {}
    season_meta: dict = {}
    calendar: list[dict] = []
    raw_season: list[dict] = []
    errors: list[str] = []

    try:
        calendar, cal_meta = await fetch_calendar()
    except BangumiFetchError as exc:
        errors.append(str(exc))

    try:
        raw_season, season_meta = await fetch_season_subjects(season_info["year"], season_info["month"])
    except BangumiFetchError as exc:
        errors.append(str(exc))

    if not raw_season:
        try:
            fb = _load_season_fallback(season_info["code"])
            raw_season = fb.get("items") or []
            season_meta = {
                "source": "fallback",
                "season_label": fb.get("season_label") or season_info["label"],
            }
            if not calendar:
                calendar = _items_to_calendar_days(raw_season)
                cal_meta = {"source": "fallback"}
        except BangumiFetchError as exc:
            errors.append(str(exc))

    if not calendar and raw_season:
        calendar = _items_to_calendar_days(raw_season)
        cal_meta.setdefault("source", "fallback")

    weekday_map = _calendar_weekday_map(calendar)
    season = [normalize_subject_item(item, weekday_map) for item in raw_season]
    season.sort(key=lambda x: (x.get("air_weekday") or 9, x.get("name_cn") or x.get("name") or ""))

    weekdays = [
        {
            "weekday": day.get("weekday"),
            "items": [
                normalize_calendar_item(i, (day.get("weekday") or {}).get("id") or 0)
                for i in day.get("items") or []
            ],
        }
        for day in calendar
    ]

    today_id = today_weekday_id()
    today_items = items_for_weekday(calendar, today_id)
    if not today_items:
        today_items = [i for i in season if i.get("air_weekday") == today_id]

    source = "live"
    if cal_meta.get("source") == "fallback" or season_meta.get("source") == "fallback":
        source = "fallback"
    elif cal_meta.get("source") == "cache" or season_meta.get("source") == "cache":
        source = "cache"

    meta = calendar_meta(calendar, {
        "source": source,
        "season_code": season_info["code"],
        "season_label": season_meta.get("season_label") or season_info["label"],
        "season_count": len(season),
        "calendar_source": cal_meta.get("source"),
        "season_source": season_meta.get("source"),
    })
    if errors and source == "fallback":
        meta["error"] = (
            "无法连接 Bangumi API，已加载 "
            f"{meta['season_label']} 离线数据（本地网络可能需代理；服务器环境通常可直连）"
        )

    season, today_items, weekdays = await enrich_schedule_watch_urls(
        season, today_items, weekdays, live_suggest=False,
    )

    season, today_items, weekdays = await localize_schedule_covers(
        season, today_items, weekdays,
    )

    result = {
        "meta": meta,
        "weekdays": weekdays,
        "season": season,
        "today_items": today_items,
    }
    _cached_set(CACHE_KEY_SCHEDULE, result, CACHE_TTL_SCHEDULE)
    return result
