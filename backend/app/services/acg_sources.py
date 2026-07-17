"""ACG 资讯 RSS 采集。

只使用 RSS 源 item 自带的真实链接，绝不编造 URL。单个源失败不影响整体。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import struct_time

import feedparser
import httpx

from app.core.config import get_settings

REQUEST_TIMEOUT = 10.0
USER_AGENT = "CYINC-Platform/1.0 (https://cyinc.ink)"

# 内置默认 RSS 源（动漫资讯 / 二游更新）。可用 ACG_RSS_FEEDS 覆盖。
# category: news=业界新闻, game=二游/游戏更新
DEFAULT_FEEDS: list[dict] = [
    {"url": "https://www.anitama.cn/feed", "source": "Anitama", "category": "news"},
    {"url": "https://www.gcores.com/rss", "source": "机核 GCORES", "category": "news"},
    {"url": "https://acg.gamer.com.tw/rss.xml", "source": "巴哈姆特 ACG", "category": "news"},
    {"url": "https://www.4gamers.com.tw/rss/latest-news", "source": "4Gamers", "category": "game"},
]


@dataclass
class RssItem:
    title: str
    link: str
    source: str
    category: str
    published: str = ""
    published_ts: float = 0.0
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "link": self.link,
            "source": self.source,
            "category": self.category,
            "published": self.published,
        }


@dataclass
class FeedResult:
    items: list[RssItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _parse_feed_config(raw: str) -> list[dict]:
    """解析 ACG_RSS_FEEDS。

    支持两种写法（逗号分隔多个）：
      - "https://a/feed"                     （仅 URL）
      - "https://a/feed|来源名|category"      （URL|来源|分类）
    """
    feeds: list[dict] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = [p.strip() for p in chunk.split("|")]
        url = parts[0]
        if not url:
            continue
        source = parts[1] if len(parts) > 1 and parts[1] else url
        category = parts[2] if len(parts) > 2 and parts[2] else "news"
        feeds.append({"url": url, "source": source, "category": category})
    return feeds


def get_configured_feeds() -> list[dict]:
    settings = get_settings()
    configured = _parse_feed_config(settings.acg_rss_feeds or "")
    return configured or DEFAULT_FEEDS


def _struct_to_iso(t: struct_time | None) -> tuple[str, float]:
    if not t:
        return "", 0.0
    try:
        dt = datetime(*t[:6], tzinfo=timezone.utc)
        return dt.date().isoformat(), dt.timestamp()
    except (ValueError, TypeError):
        return "", 0.0


async def _fetch_one(client: httpx.AsyncClient, feed: dict, per_feed_limit: int) -> FeedResult:
    result = FeedResult()
    url = feed["url"]
    source = feed.get("source") or url
    category = feed.get("category") or "news"
    try:
        resp = await client.get(url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
    except (httpx.HTTPError, Exception) as exc:  # noqa: BLE001 - 单源失败降级
        result.errors.append(f"{source}: {exc}")
        return result

    for entry in (parsed.entries or [])[:per_feed_limit]:
        title = (getattr(entry, "title", "") or "").strip()
        link = (getattr(entry, "link", "") or "").strip()
        if not title or not link:
            continue
        published_struct = getattr(entry, "published_parsed", None) or getattr(
            entry, "updated_parsed", None
        )
        published, ts = _struct_to_iso(published_struct)
        result.items.append(
            RssItem(
                title=title,
                link=link,
                source=source,
                category=category,
                published=published,
                published_ts=ts,
                summary=(getattr(entry, "summary", "") or "").strip(),
            )
        )
    return result


async def fetch_rss_items(
    feeds: list[dict] | None = None,
    *,
    per_feed_limit: int = 8,
) -> FeedResult:
    """并发抓取多个 RSS 源，返回去重后的条目 + 各源错误。"""
    feeds = feeds if feeds is not None else get_configured_feeds()
    if not feeds:
        return FeedResult()

    combined = FeedResult()
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        results = await asyncio.gather(
            *(_fetch_one(client, feed, per_feed_limit) for feed in feeds)
        )

    seen_links: set[str] = set()
    seen_titles: set[str] = set()
    for res in results:
        combined.errors.extend(res.errors)
        for item in res.items:
            key_link = item.link.lower()
            key_title = item.title.lower()
            if key_link in seen_links or key_title in seen_titles:
                continue
            seen_links.add(key_link)
            seen_titles.add(key_title)
            combined.items.append(item)

    # 有时间的按时间倒序，无时间的沉底
    combined.items.sort(key=lambda i: i.published_ts, reverse=True)
    return combined
