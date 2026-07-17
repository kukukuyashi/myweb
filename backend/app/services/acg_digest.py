"""ACG 每日资讯汇总：Bangumi 今日新番 + RSS 业界新闻/二游更新 -> Markdown。

链接一律来自数据源本身，不编造。Dify 润色为可选增强，失败则回退原始拼装文本。
"""

from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services import acg_articles, acg_sources, bangumi_client
from app.services.dify_client import DifyError, run_summary_workflow

_TZ = ZoneInfo("Asia/Shanghai")

_WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _now() -> datetime:
    try:
        return datetime.now(_TZ)
    except Exception:  # noqa: BLE001 - 本地缺 tzdata 时回退
        return datetime.now()


def _today_label(now: datetime) -> str:
    weekday = _WEEKDAY_CN[now.isoweekday() - 1]
    return f"{now.year}年{now.month}月{now.day}日 {weekday}"


def _anime_section(today_items: list[dict], season_label: str) -> str:
    lines = ["## 今日新番更新"]
    if not today_items:
        lines.append("")
        lines.append("_今天暂无排定更新的新番（或数据源未返回今日放送）。_")
        return "\n".join(lines)

    lines.append("")
    for item in today_items:
        name = item.get("name_cn") or item.get("name") or "未知作品"
        rating = item.get("rating")
        watch_url = item.get("watch_url")
        rating_txt = f" · 评分 {rating}" if rating else ""
        if watch_url:
            lines.append(f"- **{name}**{rating_txt} — [在线观看]({watch_url})")
        else:
            lines.append(f"- **{name}**{rating_txt}")
    lines.append("")
    lines.append(f"> 数据来源：Bangumi 番组计划（{season_label}）")
    return "\n".join(lines)


def _news_section(title: str, items: list[acg_sources.RssItem], empty_hint: str) -> str:
    lines = [f"## {title}"]
    lines.append("")
    if not items:
        lines.append(f"_{empty_hint}_")
        return "\n".join(lines)
    for item in items:
        date_txt = f"（{item.published}）" if item.published else ""
        lines.append(f"- [{item.title}]({item.link}) — {item.source}{date_txt}")
    return "\n".join(lines)


async def build_daily_digest(now: datetime | None = None) -> dict:
    """采集并拼装当日 ACG 资讯，返回 {title, content_md, cover_url, source_meta}。"""
    now = now or _now()
    bundle = await build_daily_bundle(now=now, use_ai=False)
    return bundle["daily"]


async def build_daily_bundle(
    now: datetime | None = None,
    *,
    use_ai: bool = False,
    article_limit: int = 3,
) -> dict:
    """采集当日全部素材，返回：
    - daily: 1 篇速报汇总（送 acg-daily 板块）
    - articles: N 篇深度图文（送 acg-news 板块）

    共用一次 RSS + Bangumi 抓取，避免重复请求。
    """
    now = now or _now()
    today_label = _today_label(now)

    # 1. Bangumi 今日新番
    today_items: list[dict] = []
    season_label = bangumi_client.current_season_info(now)["label"]
    cover_url: str | None = None
    bangumi_error = ""
    try:
        schedule = await bangumi_client.build_schedule()
        today_items = schedule.get("today_items") or []
        season_label = (schedule.get("meta") or {}).get("season_label") or season_label
        for item in today_items:
            if item.get("cover_url"):
                cover_url = item["cover_url"]
                break
    except Exception as exc:  # noqa: BLE001 - 采集失败降级
        bangumi_error = str(exc)

    # 2. RSS 新闻 / 二游更新（一次抓取，速报和深度文都从这批里选）
    feed_result = await acg_sources.fetch_rss_items()
    news_items = [i for i in feed_result.items if i.category != "game"]
    game_items = [i for i in feed_result.items if i.category == "game"]
    news_top = news_items[:12]
    game_top = game_items[:10]

    # 3. 速报 Markdown
    parts = [
        f"# {season_label}·每日 ACG 资讯（{today_label}）",
        "",
        _anime_section(today_items, season_label),
        "",
        _news_section("业界新闻", news_top, "今日暂未采集到业界新闻。"),
        "",
        _news_section("二游更新", game_top, "今日暂未采集到二游更新公告。"),
        "",
        "---",
        f"_本帖由 ACG 资讯机器人自动汇总于 {today_label}，链接均来自公开数据源。_",
    ]
    daily_content = "\n".join(parts)

    daily_source_meta = {
        "generated_at": now.isoformat(),
        "season_label": season_label,
        "anime_count": len(today_items),
        "anime": [
            {
                "name": i.get("name_cn") or i.get("name"),
                "watch_url": i.get("watch_url"),
                "rating": i.get("rating"),
            }
            for i in today_items
        ],
        "news": [i.to_dict() for i in news_top],
        "game": [i.to_dict() for i in game_top],
        "feed_errors": feed_result.errors,
    }
    if bangumi_error:
        daily_source_meta["bangumi_error"] = bangumi_error

    daily = {
        "title": f"【每日速报】{season_label} · {today_label} ACG 资讯汇总",
        "content_md": daily_content,
        "cover_url": cover_url,
        "source_meta": json.dumps(daily_source_meta, ensure_ascii=False),
    }

    # 4. 深度文章：从新闻+游戏池里挑热门，AI 展开
    article_pool = news_items + game_items
    hot_drafts = await acg_articles.build_hot_articles(
        article_pool, limit=article_limit, use_ai=use_ai
    )
    articles: list[dict] = []
    for d in hot_drafts:
        articles.append(
            {
                "title": d.title,
                "content_md": d.content_md,
                "cover_url": d.cover_url,
                "source_meta": json.dumps(
                    {
                        "kind": "article",
                        "source": d.source_name,
                        "link": d.source_link,
                        "generated_at": now.isoformat(),
                        "used_ai": use_ai,
                    },
                    ensure_ascii=False,
                ),
            }
        )

    return {
        "daily": daily,
        "articles": articles,
        "meta": {
            "season_label": season_label,
            "today_label": today_label,
            "news_count": len(news_items),
            "game_count": len(game_items),
            "anime_count": len(today_items),
            "article_count": len(articles),
        },
    }


async def polish_with_dify(title: str, content_md: str) -> str:
    """可选：用 Dify 摘要 Workflow 润色导语。失败则原样返回。"""
    try:
        outputs = await run_summary_workflow(title=title, content=content_md)
    except DifyError:
        return content_md
    except Exception:  # noqa: BLE001 - 润色为增强项，任何异常都不阻断
        return content_md

    summary = (outputs.get("summary") or "").strip()
    if not summary:
        return content_md
    intro = f"> **今日导读**：{summary}\n\n"
    return intro + content_md
