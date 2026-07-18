"""基于 RSS 热门条目生成深度图文文章（图片来自 RSS content / media，绝不编造）。

关键约束：
- 图片和事实链接一律来自 RSS 原文，绝不编造。
- Dify 展开只做"围绕给定事实的中文点评/背景补充"，任何链接/数据必须与原文一致。
- Dify 挂了自动降级：用 正文纯文本 + 原文链接 + 抓到的图片。
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from app.services.acg_sources import RssItem
from app.services.dify_client import DifyError, run_summary_workflow

# <img src="...">
_IMG_SRC_RE = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)
# 4Gamers 等站点的原图属性
_RAW_SRC_RE = re.compile(
    r"""data-(?:puku-raw-src|src|original|lazy-src)=["']([^"']+)["']""",
    re.IGNORECASE,
)
# <source srcset="url1 800w, url2 1200w">
_SRCSET_RE = re.compile(r"""srcset=["']([^"']+)["']""", re.IGNORECASE)
_OG_IMAGE_RE = re.compile(
    r"""<meta[^>]+(?:property|name)=["']og:image(?::url)?["'][^>]+content=["']([^"']+)["']"""
    r"""|<meta[^>]+content=["']([^"']+)["'][^>]+(?:property|name)=["']og:image(?::url)?["']""",
    re.IGNORECASE,
)
# 去 HTML 标签
_TAG_RE = re.compile(r"<[^>]+>")
# 折叠空白
_WS_RE = re.compile(r"\s+")

_SKIP_URL_HINTS = ("1x1", "pixel", "spacer", "blank.gif", "tracking")
_PAGE_FETCH_TIMEOUT = 8.0
_USER_AGENT = "CYINC-Platform/1.0 (https://cyinc.ink)"


@dataclass
class ArticleDraft:
    title: str
    content_md: str
    cover_url: str | None
    source_link: str
    source_name: str


def _strip_html(text: str) -> str:
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    return text.strip()


def _normalize_img_url(url: str, base: str = "") -> str | None:
    if not url:
        return None
    url = html.unescape(url.strip())
    if not url or url.startswith("data:"):
        return None
    if url.startswith("//"):
        url = "https:" + url
    if url.startswith("/") and base:
        url = urljoin(base, url)
    if not url.startswith(("http://", "https://")):
        return None
    low = url.lower()
    if any(h in low for h in _SKIP_URL_HINTS):
        return None
    # 过滤非图片常见脚本/widget
    path = urlparse(url).path.lower()
    if path.endswith((".js", ".css", ".html", ".htm", ".xml")):
        return None
    return url


def _srcset_first(srcset: str) -> str | None:
    """取 srcset 里第一张候选 URL。"""
    if not srcset:
        return None
    first = srcset.split(",")[0].strip().split()[0] if srcset.strip() else ""
    return first or None


def _extract_images(html_blob: str, *, base: str = "", extra: list[str] | None = None) -> list[str]:
    """从 HTML + media URL 列表抽取配图，优先原图属性。"""
    found: list[str] = []
    seen: set[str] = set()

    def add(raw: str | None) -> None:
        url = _normalize_img_url(raw or "", base=base)
        if not url or url in seen:
            return
        seen.add(url)
        found.append(url)

    # 1) 结构化 media（封面常在这里）
    for u in extra or []:
        add(u)

    if html_blob:
        # 2) data-*-src 原图（优于 thumbor 压缩链）
        for m in _RAW_SRC_RE.finditer(html_blob):
            add(m.group(1))
        # 3) 普通 img src
        for m in _IMG_SRC_RE.finditer(html_blob):
            add(m.group(1))
        # 4) picture/source srcset
        for m in _SRCSET_RE.finditer(html_blob):
            add(_srcset_first(m.group(1)))

    return found


async def _fetch_page_images(page_url: str, *, limit: int = 4) -> list[str]:
    """RSS 无图时回落抓取原文页 og:image / 首批 <img>（失败则空列表）。"""
    if not page_url.startswith(("http://", "https://")):
        return []
    try:
        import httpx

        async with httpx.AsyncClient(
            timeout=_PAGE_FETCH_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        ) as client:
            resp = await client.get(page_url)
            resp.raise_for_status()
            html_text = resp.text[:400_000]
    except Exception:  # noqa: BLE001
        return []

    found: list[str] = []
    seen: set[str] = set()

    def add(raw: str | None) -> None:
        url = _normalize_img_url(raw or "", base=page_url)
        if not url or url in seen:
            return
        seen.add(url)
        found.append(url)

    for m in _OG_IMAGE_RE.finditer(html_text):
        add(m.group(1) or m.group(2))
    for m in _RAW_SRC_RE.finditer(html_text):
        add(m.group(1))
        if len(found) >= limit:
            return found
    for m in _IMG_SRC_RE.finditer(html_text):
        add(m.group(1))
        if len(found) >= limit:
            break
    return found[:limit]


def _body_text_for_article(item: RssItem) -> str:
    """优先用 content HTML 抽正文；过长则截到约 1200 字。"""
    raw = _strip_html(item.content_html) if item.content_html else ""
    short = _strip_html(item.summary)
    text = raw if len(raw) >= len(short) else short
    if not text:
        return ""
    if len(text) <= 1200:
        return text
    cut = text[:1200]
    # 尽量在句号处截断
    for sep in ("。", "！", "？", ". ", "! ", "? "):
        idx = cut.rfind(sep)
        if idx >= 400:
            return cut[: idx + len(sep.strip())].strip()
    return cut.rstrip() + "…"


def pick_hot_items(items: list[RssItem], limit: int = 3) -> list[RssItem]:
    """选取"热门"：优先带图 + 摘要长的 + 时间近。避免同源霸榜。"""
    scored: list[tuple[float, int, RssItem]] = []
    for idx, it in enumerate(items):
        html_blob = it.content_html or it.summary
        images = _extract_images(html_blob, base=it.link, extra=it.media_urls)
        summary_len = len(_body_text_for_article(it))
        score = 0.0
        if images:
            score += 2.0
        if summary_len >= 400:
            score += 1.5
        elif summary_len >= 120:
            score += 0.8
        if it.published_ts:
            score += 0.3
        score += max(0.0, 0.5 - idx * 0.02)
        scored.append((score, idx, it))

    scored.sort(key=lambda x: (-x[0], x[1]))

    picked: list[RssItem] = []
    used_sources: dict[str, int] = {}
    for _, _, it in scored:
        if used_sources.get(it.source, 0) >= 2:
            continue
        picked.append(it)
        used_sources[it.source] = used_sources.get(it.source, 0) + 1
        if len(picked) >= limit:
            break

    if len(picked) < limit:
        for _, _, it in scored:
            if it in picked:
                continue
            picked.append(it)
            if len(picked) >= limit:
                break
    return picked


def _fallback_article(item: RssItem, images: list[str], summary_text: str) -> str:
    """Dify 未启用/失败时的兜底：事实 + 配图 + 原文链接。"""
    lines: list[str] = []
    if images:
        lines.append(
            f"> 本文由 ACG 资讯姬整理，事实与图片均来自原文：[{item.source}]({item.link})"
        )
    else:
        lines.append(
            f"> 本文由 ACG 资讯姬整理，事实来自原文：[{item.source}]({item.link})"
        )
    lines.append("")

    if images:
        lines.append(f"![封面]({images[0]})")
        lines.append("")

    if summary_text:
        lines.append("## 内容概览")
        lines.append("")
        lines.append(summary_text)
        lines.append("")

    if len(images) > 1:
        lines.append("## 相关配图")
        lines.append("")
        for i, img in enumerate(images[1:5], start=2):
            lines.append(f"![配图 {i}]({img})")
            lines.append("")

    if item.published:
        lines.append(f"发布日期：{item.published}")
        lines.append("")

    lines.append("## 原文来源")
    lines.append("")
    lines.append(f"- 出处：**{item.source}**")
    lines.append(f"- 原文链接：<{item.link}>")
    lines.append("")
    lines.append("---")
    if images:
        lines.append("_点击原文链接可查看完整报道与更多配图。_")
    else:
        lines.append("_原文未提供可引用配图；点击原文链接查看完整报道。_")
    return "\n".join(lines)


async def _polish_article_with_dify(item: RssItem, summary_text: str) -> str | None:
    """尝试用 Dify 展开中文详细正文。失败返回 None。"""
    prompt_content = (
        "你是一个严谨的 ACG 资讯编辑。请基于下面**已核实**的事实素材，"
        "写一篇 500-900 字的中文详细资讯稿，风格自然但专业。\n\n"
        "**硬性要求**（违反即视为失败）：\n"
        "1. 只能使用素材里出现过的事实、人名、作品名、数字、日期；素材里没有的一律不要写。\n"
        "2. 不要编造任何链接；如需引用出处只写「据 <来源名> 报道」。\n"
        "3. 不要输出任何 Markdown 图片语法或 <img>；配图我会自己插入。\n"
        "4. 输出结构：一段导语 → 2-4 个 `## 小节标题` → 简短结语。\n"
        "5. 结尾不要加「关注我们」「感谢阅读」等口水话。\n\n"
        f"---素材开始---\n"
        f"标题：{item.title}\n"
        f"来源：{item.source}\n"
        f"发布日期：{item.published or '未提供'}\n"
        f"原文摘要（已去 HTML）：\n{summary_text or '（原文未提供正文摘要）'}\n"
        f"---素材结束---\n\n"
        "请直接输出正文 Markdown，不要复述以上要求。"
    )
    try:
        outputs = await run_summary_workflow(title=item.title, content=prompt_content)
    except DifyError:
        return None
    except Exception:  # noqa: BLE001 - Dify 失败一律降级
        return None

    summary = (outputs.get("summary") or outputs.get("text") or "").strip()
    if len(summary) < 120:
        return None
    return summary


def _assemble_article(item: RssItem, images: list[str], body_md: str) -> str:
    parts: list[str] = []
    if images:
        parts.append(f"![封面]({images[0]})")
        parts.append("")
    parts.append(body_md.strip())
    parts.append("")
    extra_imgs = images[1:5]
    if extra_imgs:
        parts.append("## 配图")
        parts.append("")
        for i, img in enumerate(extra_imgs, start=2):
            parts.append(f"![配图 {i}]({img})")
            parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("### 原文出处")
    parts.append("")
    parts.append(f"- 来源：**{item.source}**")
    if item.published:
        parts.append(f"- 日期：{item.published}")
    parts.append(f"- 原文链接：<{item.link}>")
    parts.append("")
    if images:
        parts.append("_本文由 ACG 资讯姬基于以上出处整理与展开，事实与图片均可回溯到原文。_")
    else:
        parts.append("_本文由 ACG 资讯姬基于以上出处整理与展开；原文未提供可引用配图。_")
    return "\n".join(parts)


async def build_article_draft(item: RssItem, *, use_ai: bool) -> ArticleDraft:
    """把单条 RSS item 转成一篇深度草稿。"""
    html_blob = item.content_html or item.summary
    images = _extract_images(html_blob, base=item.link, extra=item.media_urls)
    if not images:
        images = await _fetch_page_images(item.link)
    summary_text = _body_text_for_article(item)

    body_md: str | None = None
    if use_ai and summary_text:
        body_md = await _polish_article_with_dify(item, summary_text)

    if body_md:
        content_md = _assemble_article(item, images, body_md)
    else:
        content_md = _fallback_article(item, images, summary_text)

    title = item.title.strip() or f"{item.source} · 未命名资讯"
    if not title.startswith(("【", "「")):
        title = f"【{item.source}】{title}"

    return ArticleDraft(
        title=title,
        content_md=content_md,
        cover_url=images[0] if images else None,
        source_link=item.link,
        source_name=item.source,
    )


async def build_hot_articles(
    all_rss_items: list[RssItem],
    *,
    limit: int = 3,
    use_ai: bool = False,
) -> list[ArticleDraft]:
    hot = pick_hot_items(all_rss_items, limit=limit)
    drafts: list[ArticleDraft] = []
    for item in hot:
        try:
            drafts.append(await build_article_draft(item, use_ai=use_ai))
        except Exception:  # noqa: BLE001 - 单条失败不影响其他
            continue
    return drafts
