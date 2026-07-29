"""追番封面本地缓存：把 Bangumi 的封面下载到我们自己的 /uploads/anime，避免外链盗链/防盗链导致的封面丢失。

思路：封面 URL 用 sha1 生成确定性文件名；已存在则直接复用（跨多次重建都不用再下载）。
下载失败时保留原始外链兜底，下次重建再重试。
"""
import asyncio
import hashlib
import logging
from pathlib import Path

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

COVER_SUBDIR = "anime"
COVER_TIMEOUT = 8.0
COVER_CONCURRENCY = 8
MAX_COVER_BYTES = 4 * 1024 * 1024
# 服务器端下载 bgm 封面：带 Referer + 浏览器 UA，绕过防盗链。
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://bgm.tv/",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}

_EXT_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _cover_dir() -> Path:
    dest = Path(get_settings().upload_dir) / COVER_SUBDIR
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def _is_external(url: str | None) -> bool:
    return bool(url) and url.startswith(("http://", "https://"))


def _sniff_ext(data: bytes) -> str | None:
    if len(data) < 12:
        return None
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


def _existing_local(digest: str) -> str | None:
    dest_dir = _cover_dir()
    for ext in (".jpg", ".png", ".webp", ".gif"):
        if (dest_dir / f"{digest}{ext}").is_file():
            return f"/uploads/{COVER_SUBDIR}/{digest}{ext}"
    return None


async def _download_one(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore) -> tuple[str, str | None]:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    cached = _existing_local(digest)
    if cached:
        return url, cached
    async with sem:
        try:
            res = await client.get(url, headers=_HEADERS)
            res.raise_for_status()
            data = res.content
        except Exception as exc:  # noqa: BLE001 - 单张失败不影响整体
            logger.info("cover cache download failed %s: %s", url, exc)
            return url, None
    if not data or len(data) > MAX_COVER_BYTES:
        return url, None
    ext = _sniff_ext(data) or _EXT_BY_CONTENT_TYPE.get(
        (res.headers.get("content-type") or "").split(";")[0].strip().lower()
    )
    if not ext:
        return url, None
    dest = _cover_dir() / f"{digest}{ext}"
    try:
        dest.write_bytes(data)
    except OSError as exc:
        logger.warning("cover cache write failed %s: %s", dest, exc)
        return url, None
    return url, f"/uploads/{COVER_SUBDIR}/{digest}{ext}"


async def cache_cover_urls(urls: list[str]) -> dict[str, str]:
    """下载一批外链封面，返回 {原始URL: 本地路径}。失败的不出现在返回里。"""
    unique = {u for u in urls if _is_external(u)}
    if not unique:
        return {}
    sem = asyncio.Semaphore(COVER_CONCURRENCY)
    mapping: dict[str, str] = {}
    async with httpx.AsyncClient(timeout=COVER_TIMEOUT, follow_redirects=True) as client:
        results = await asyncio.gather(
            *(_download_one(client, u, sem) for u in unique),
            return_exceptions=True,
        )
    for item in results:
        if isinstance(item, tuple):
            url, local = item
            if local:
                mapping[url] = local
    return mapping


def _rewrite_items(items: list[dict], mapping: dict[str, str]) -> None:
    for it in items:
        local = mapping.get(it.get("cover_url"))
        if local:
            it["cover_url"] = local


async def localize_schedule_covers(
    season: list[dict],
    today_items: list[dict],
    weekdays: list[dict],
) -> tuple[list[dict], list[dict], list[dict]]:
    """把追番表里所有封面外链替换成本地缓存路径（下载失败的保留原链）。"""
    urls: list[str] = []
    urls.extend(i.get("cover_url") for i in season)
    urls.extend(i.get("cover_url") for i in today_items)
    for day in weekdays:
        urls.extend(i.get("cover_url") for i in (day.get("items") or []))
    try:
        mapping = await cache_cover_urls([u for u in urls if u])
    except Exception as exc:  # noqa: BLE001 - 缓存失败不影响返回数据
        logger.warning("cover cache batch failed: %s", exc)
        return season, today_items, weekdays
    if not mapping:
        return season, today_items, weekdays
    _rewrite_items(season, mapping)
    _rewrite_items(today_items, mapping)
    for day in weekdays:
        _rewrite_items(day.get("items") or [], mapping)
    return season, today_items, weekdays