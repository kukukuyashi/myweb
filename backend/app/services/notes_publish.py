"""Publish Markdown notes to Content/*.html + posts.json."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from app.services.notes_markdown import (
    build_article_html,
    extract_date_from_body,
    extract_title_from_body,
    infer_excerpt,
    markdown_to_html,
    parse_frontmatter,
    parse_tags,
    today_iso,
)
from app.services.notes_paths import content_dir, site_web_root
from app.services.posts_catalog import load_posts, save_posts, upsert_post

_PRERENDER_MAIN = re.compile(
    r'(<main class="prerender-fallback"[^>]*>)\s*.*?\s*(<p class="prerender-note">)',
    re.S,
)


def resolve_post_meta(
    *,
    meta: dict[str, Any],
    body: str,
    md_path: Path,
    posts: list[dict[str, Any]],
    defaults: dict[str, Any] | None = None,
) -> dict[str, Any]:
    defaults = defaults or {}
    base_name = md_path.stem
    html_file = meta.get("file") or f"{base_name}.html"
    file_name = html_file if str(html_file).endswith(".html") else f"{html_file}.html"
    existing = next((p for p in posts if p.get("file") == file_name), None)

    title = (
        meta.get("title")
        or extract_title_from_body(body)
        or (existing or {}).get("title")
        or defaults.get("title")
        or base_name
    )
    date_str = (
        meta.get("date")
        or extract_date_from_body(body)
        or (existing or {}).get("date")
        or defaults.get("date")
        or today_iso()
    )
    category = (
        meta.get("category")
        or (existing or {}).get("category")
        or defaults.get("category")
        or "学习"
    )
    if meta.get("tags") is not None:
        tags = parse_tags(meta.get("tags"))
    elif (existing or {}).get("tags"):
        tags = list(existing["tags"])
    else:
        tags = parse_tags(defaults.get("tags") or category)
    excerpt = (
        meta.get("excerpt")
        or (existing or {}).get("excerpt")
        or defaults.get("excerpt")
        or infer_excerpt(body, str(title))
    )
    cover = meta.get("cover") or (existing or {}).get("cover") or defaults.get("cover") or ""
    post_id = (existing or {}).get("id") or (max([int(p.get("id") or 0) for p in posts] + [0]) + 1)

    post: dict[str, Any] = {
        "id": int(post_id),
        "title": str(title),
        "date": str(date_str),
        "category": str(category),
        "tags": tags,
        "excerpt": str(excerpt),
        "file": file_name,
    }
    if cover:
        post["cover"] = cover
    return post


def get_note_publish_status(rel_path: str, posts: list[dict[str, Any]]) -> dict[str, Any]:
    from app.services.notes_store import assert_note_abs, is_draft_path

    abs_path = assert_note_abs(rel_path)
    meta, body = parse_frontmatter(abs_path.read_text(encoding="utf-8"))
    preview = resolve_post_meta(meta=meta, body=body, md_path=abs_path, posts=posts)
    html_path = content_dir() / preview["file"]
    published = any(p.get("file") == preview["file"] for p in posts)

    status = "draft"
    if published:
        status = "published"
        if html_path.is_file():
            if abs_path.stat().st_mtime > html_path.stat().st_mtime + 1:
                status = "modified"
        else:
            status = "modified"
    elif is_draft_path(rel_path):
        status = "draft"

    return {
        "status": status,
        "post": preview,
        "postId": preview["id"],
        "htmlFile": preview["file"],
    }


def update_prerender_article(post: dict[str, Any], article_html: str) -> Path | None:
    """Refresh SEO fallback so /content/{id} shows the latest body before SPA hydrates."""
    post_id = post.get("id")
    if post_id is None:
        return None
    prerender = site_web_root() / "content" / str(post_id) / "index.html"
    if not prerender.is_file():
        return None
    meta = f"{post.get('date') or ''} · {post.get('category') or ''}".strip(" ·")
    inner = (
        f"<h1>{html.escape(str(post.get('title') or ''))}</h1>\n"
        f'<p class="prerender-meta">{html.escape(meta)}</p>\n'
        f'<div class="prerender-article">{article_html}</div>'
    )
    text = prerender.read_text(encoding="utf-8")

    def _repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}\n{inner}\n      {match.group(2)}"

    new_text, n = _PRERENDER_MAIN.subn(_repl, text, count=1)
    if not n:
        return None
    prerender.write_text(new_text, encoding="utf-8")
    return prerender


def publish_markdown_file(rel_path: str, posts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    from app.services.notes_store import assert_note_abs

    posts = list(posts if posts is not None else load_posts())
    abs_path = assert_note_abs(rel_path)
    if not abs_path.is_file():
        raise FileNotFoundError("笔记不存在")

    meta, body = parse_frontmatter(abs_path.read_text(encoding="utf-8"))
    post = resolve_post_meta(meta=meta, body=body, md_path=abs_path, posts=posts)
    body_html = markdown_to_html(body)
    article_html = build_article_html(
        title=post["title"],
        date_str=post["date"],
        excerpt=post["excerpt"],
        body_html=body_html,
    )

    out_dir = content_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / post["file"]
    existed = any(p.get("file") == post["file"] for p in posts)
    html_path.write_text(article_html, encoding="utf-8")

    next_posts = upsert_post(posts, post)
    save_posts(next_posts)
    prerender_path = update_prerender_article(post, article_html)
    return {
        "post": post,
        "htmlPath": str(html_path),
        "prerenderPath": str(prerender_path) if prerender_path else None,
        "updated": existed,
        "posts": next_posts,
    }


def preview_markdown(*, meta: dict[str, Any], body: str) -> str:
    title = meta.get("title") or "预览"
    date_str = meta.get("date") or today_iso()
    excerpt = meta.get("excerpt") or ""
    body_html = markdown_to_html(body or "")
    return build_article_html(title=title, date_str=date_str, excerpt=excerpt, body_html=body_html)
