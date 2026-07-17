"""基于 RSS 热门条目生成深度图文文章（图片来自 item summary 里的真实 <img src>）。

关键约束：
- 图片和事实链接一律来自 RSS 原文，绝不编造。
- Dify 展开只做"围绕给定事实的中文点评/背景补充"，任何链接/数据必须与原文一致。
- Dify 挂了自动降级：只用 摘要纯文本 + 原文链接 + 抓到的图片。
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from app.services.acg_sources import RssItem
from app.services.dify_client import DifyError, run_summary_workflow

# 抓 <img src="...">（HTML/RSS 都能命中）
_IMG_RE = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)
# 去 HTML 标签
_TAG_RE = re.compile(r"<[^>]+>")
# 折叠空白
_WS_RE = re.compile(r"\s+")


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


def _extract_images(summary_html: str) -> list[str]:
    if not summary_html:
        return []
    found: list[str] = []
    seen: set[str] = set()
    for m in _IMG_RE.finditer(summary_html):
        url = html.unescape(m.group(1).strip())
        if not url.startswith(("http://", "https://")):
            continue
        if url in seen:
            continue
        seen.add(url)
        found.append(url)
    return found


def pick_hot_items(items: list[RssItem], limit: int = 3) -> list[RssItem]:
    """选取"热门"：优先带图 + 摘要长的 + 时间近。避免同源霸榜。"""
    scored: list[tuple[float, int, RssItem]] = []
    for idx, it in enumerate(items):
        images = _extract_images(it.summary)
        summary_len = len(_strip_html(it.summary))
        # 分数：有图 +2；摘要长度分档；带时间戳的按新旧微调；越靠前的原始位置越占优
        score = 0.0
        if images:
            score += 2.0
        if summary_len >= 400:
            score += 1.5
        elif summary_len >= 120:
            score += 0.8
        if it.published_ts:
            score += 0.3
        # 原始位置微调（越靠前越好）
        score += max(0.0, 0.5 - idx * 0.02)
        scored.append((score, idx, it))

    scored.sort(key=lambda x: (-x[0], x[1]))

    picked: list[RssItem] = []
    used_sources: dict[str, int] = {}
    for _, _, it in scored:
        # 每个源最多贡献 2 条，避免整版都是同一来源
        if used_sources.get(it.source, 0) >= 2:
            continue
        picked.append(it)
        used_sources[it.source] = used_sources.get(it.source, 0) + 1
        if len(picked) >= limit:
            break

    # 备份：极端情况数据不够，硬凑到 limit（可能会跨源上限）
    if len(picked) < limit:
        for _, _, it in scored:
            if it in picked:
                continue
            picked.append(it)
            if len(picked) >= limit:
                break
    return picked


def _fallback_article(item: RssItem, images: list[str], summary_text: str) -> str:
    """Dify 未启用/失败时的兜底：仅陈述事实 + 原文链接 + 图片，不做主观扩写。"""
    lines: list[str] = []
    lines.append(f"> 本文由 ACG 资讯机器人整理，事实与图片均来自原文：[{item.source}]({item.link})")
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
        for img in images[1:4]:
            lines.append(f"![图]({img})")
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
    lines.append("_由于未启用 AI 展开，本文仅呈现原始事实。点击原文链接查看完整报道。_")
    return "\n".join(lines)


async def _polish_article_with_dify(item: RssItem, summary_text: str) -> str | None:
    """尝试用 Dify 展开中文详细正文。失败返回 None。

    严格 Prompt：不允许编造事实、链接、数据；如信息不足就明确写"原文未提供"。
    """
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
    if len(summary) < 120:  # 太短的判定为无效展开
        return None
    return summary


def _assemble_article(item: RssItem, images: list[str], body_md: str) -> str:
    parts: list[str] = []
    if images:
        parts.append(f"![封面]({images[0]})")
        parts.append("")
    parts.append(body_md.strip())
    parts.append("")
    # 内嵌 2-3 张剩余图片作为版式素材
    extra_imgs = images[1:4]
    if extra_imgs:
        parts.append("## 配图")
        parts.append("")
        for img in extra_imgs:
            parts.append(f"![图]({img})")
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
    parts.append("_本文由 ACG 资讯机器人基于以上出处整理与展开，事实与图片均可回溯到原文。_")
    return "\n".join(parts)


async def build_article_draft(item: RssItem, *, use_ai: bool) -> ArticleDraft:
    """把单条 RSS item 转成一篇深度草稿。"""
    images = _extract_images(item.summary)
    summary_text = _strip_html(item.summary)

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
