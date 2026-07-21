"""Markdown frontmatter + lightweight Markdown→HTML (aligned with scripts/lib)."""

from __future__ import annotations

import re
from datetime import date
from html import escape
from typing import Any


COMMON_CATEGORIES = ["前端", "项目", "部署", "Agent", "Java", "学习", "技术", "小知识"]


def today_iso() -> str:
    return date.today().isoformat()


def parse_tags(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1]
        parts = []
        for part in re.split(r",", inner):
            p = part.strip().strip("'").strip('"')
            if p:
                parts.append(p)
        return parts
    return [t.strip() for t in re.split(r"[,，]", text) if t.strip()]


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    normalized = text.lstrip("\ufeff")
    if not normalized.startswith("---\n"):
        return {}, normalized
    end = normalized.find("\n---\n", 4)
    if end == -1:
        return {}, normalized
    raw = normalized[4:end]
    body = normalized[end + 5 :]
    meta: dict[str, Any] = {}
    for line in raw.split("\n"):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        colon = trimmed.find(":")
        if colon == -1:
            continue
        key = trimmed[:colon].strip()
        value = trimmed[colon + 1 :].strip()
        if value.startswith("[") and value.endswith("]"):
            meta[key] = parse_tags(value)
            continue
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        meta[key] = value
    return meta, body


def extract_title_from_body(body: str) -> str:
    m = re.search(r"^#\s+(.+)$", body, flags=re.M)
    return m.group(1).strip() if m else ""


def extract_date_from_body(body: str) -> str:
    m = re.search(r"^>\s*日期[：:]\s*(\d{4}-\d{2}-\d{2})", body, flags=re.M)
    return m.group(1) if m else ""


def infer_excerpt(body: str, title: str) -> str:
    for line in body.split("\n"):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#") or trimmed.startswith(">"):
            continue
        if trimmed in ("---",) or trimmed.startswith("```") or trimmed.startswith("|"):
            continue
        text = re.sub(r"^-\s+", "", trimmed)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = text.replace("**", "").replace("`", "")
        if text:
            return text[:140]
    return f"{title} — 学习笔记。"


# URL 段：允许一层括号，如 ./01-准备工作(部署笔记).md 或 /myweb/content/31
_MD_URL = r"(?:[^()\s]|\([^)]*\))+"


def _inline(s: str) -> str:
    out = escape(s)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(
        rf"!\[([^\]]*)\]\(({_MD_URL})\)",
        r'<img src="\2" alt="\1" loading="lazy" />',
        out,
    )
    out = re.sub(
        rf"\[([^\]]+)\]\(({_MD_URL})\)",
        r'<a href="\2">\1</a>',
        out,
    )
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out


def markdown_to_html(md: str) -> str:
    lines = md.lstrip("\ufeff").split("\n")
    out: list[str] = []
    in_code = False
    code_lang = ""
    in_table = False
    ul_items: list[str] = []
    ol_items: list[str] = []

    def close_lists() -> None:
        nonlocal ul_items, ol_items
        if ul_items:
            out.append("<ul>")
            out.extend(f"<li>{_inline(i)}</li>" for i in ul_items)
            out.append("</ul>")
            ul_items = []
        if ol_items:
            out.append("<ol>")
            out.extend(f"<li>{_inline(i)}</li>" for i in ol_items)
            out.append("</ol>")
            ol_items = []

    for line in lines:
        if line.startswith("```"):
            close_lists()
            if not in_code:
                in_code = True
                code_lang = line[3:].strip() or "javascript"
                out.append(f'<pre><code class="language-{escape(code_lang)}">')
            else:
                in_code = False
                out.append("</code></pre>")
            continue
        if in_code:
            out.append(escape(line))
            continue

        if line.startswith("|") and "|" in line[1:]:
            close_lists()
            if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                in_table = True
                out.append("<table><thead><tr>")
                out.extend(f"<th>{_inline(c)}</th>" for c in cells)
                out.append("</tr></thead><tbody>")
                continue
            out.append("<tr>")
            out.extend(f"<td>{_inline(c)}</td>" for c in cells)
            out.append("</tr>")
            continue
        if in_table:
            out.append("</tbody></table>")
            in_table = False

        if line.startswith("# "):
            close_lists()
            out.append(f"<h1>{_inline(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            close_lists()
            out.append(f"<h2>{_inline(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            close_lists()
            out.append(f"<h3>{_inline(line[4:].strip())}</h3>")
        elif line.startswith("> "):
            close_lists()
            out.append(f"<blockquote>{_inline(line[2:].strip())}</blockquote>")
        elif line.strip() == "---":
            close_lists()
            out.append("<hr>")
        elif re.match(r"^[-*]\s+", line):
            close_lists() if ol_items else None
            if ol_items:
                close_lists()
            ul_items.append(re.sub(r"^[-*]\s+", "", line))
        elif re.match(r"^\d+\.\s+", line):
            if ul_items:
                close_lists()
            ol_items.append(re.sub(r"^\d+\.\s+", "", line))
        elif not line.strip():
            close_lists()
        else:
            close_lists()
            out.append(f"<p>{_inline(line.strip())}</p>")

    close_lists()
    if in_table:
        out.append("</tbody></table>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def build_article_html(*, title: str, date_str: str, excerpt: str, body_html: str) -> str:
    parts: list[str] = []
    if excerpt:
        parts.append(f'<p class="article-intro">{escape(excerpt)}</p>')
    if not re.search(r"<h1[\s>]", body_html.strip(), flags=re.I):
        parts.append(f"<h1>{escape(title)}</h1>")
        parts.append(f"<blockquote>日期：{escape(date_str)}</blockquote>")
        parts.append("<hr>")
    parts.append(body_html.strip())
    return "\n".join(parts) + "\n"


def serialize_note(*, meta: dict[str, Any], body: str) -> str:
    import json

    lines = ["---"]
    order = ["title", "date", "category", "tags", "excerpt", "cover", "file"]
    keys = list(dict.fromkeys([*order, *meta.keys()]))
    for key in keys:
        value = meta.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, list):
            lines.append(
                f"{key}: [{', '.join(json.dumps(str(v), ensure_ascii=False) for v in value)}]"
            )
        else:
            lines.append(f"{key}: {json.dumps(str(value), ensure_ascii=False)}")
    lines.extend(["---", ""])
    normalized_body = str(body or "").lstrip("\n")
    return "\n".join(lines) + normalized_body
