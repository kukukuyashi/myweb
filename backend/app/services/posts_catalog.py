"""Runtime posts catalog: myweb/data/posts.json (or public/data locally)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.services.notes_paths import content_dir, posts_json_path


SKIP_HTML = {"try.html", "index.html"}


def load_posts() -> list[dict[str, Any]]:
    path = posts_json_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    posts = data.get("posts") if isinstance(data, dict) else data
    if not isinstance(posts, list):
        return []
    return [p for p in posts if isinstance(p, dict) and p.get("file")]


def save_posts(posts: list[dict[str, Any]]) -> Path:
    path = posts_json_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"posts": posts}
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def upsert_post(posts: list[dict[str, Any]], post: dict[str, Any]) -> list[dict[str, Any]]:
    next_posts = [p for p in posts if p.get("file") != post["file"]]
    next_posts.insert(0, post)
    next_posts.sort(key=lambda p: str(p.get("date") or ""), reverse=True)
    return next_posts


def remove_post_by_file(posts: list[dict[str, Any]], file_name: str) -> tuple[list[dict[str, Any]], bool]:
    before = len(posts)
    next_posts = [p for p in posts if p.get("file") != file_name]
    return next_posts, len(next_posts) < before


def list_content_html_files() -> list[str]:
    folder = content_dir()
    if not folder.is_dir():
        return []
    return sorted(
        [
            name
            for name in folder.iterdir()
            if name.is_file() and name.suffix == ".html" and name.name not in SKIP_HTML
        ],
        key=lambda p: p.name,
    )


def _infer_category(title: str, file: str) -> str:
    hay = f"{title} {file}"
    if re.search(r"Agent|LLM|Skill|MCP", hay, re.I):
        return "Agent"
    if re.search(r"Java(?!Script)", hay, re.I) or re.match(r"JAVA", file, re.I):
        return "Java"
    if re.search(r"Twikoo|GitHub Actions|部署|重构|音乐室|FLAC|Pages", hay, re.I):
        return "部署"
    if re.search(r"Flask|项目|帕朵|陈皮|root", hay, re.I):
        return "项目"
    if re.search(r"Vue|Canvas|墨染|Web API|JS|前端|RhinoWeb|Three", hay, re.I):
        return "前端"
    return "学习"


def parse_html_article_meta(html: str, file: str) -> dict[str, Any]:
    from app.services.notes_markdown import today_iso

    base = Path(file).stem
    title_m = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.I)
    intro_m = re.search(r'<p class="article-intro">([\s\S]*?)</p>', html, re.I)
    date_m = re.search(r"日期[：:]\s*(\d{4}-\d{2}-\d{2})", html)
    title = (title_m.group(1).replace("&amp;", "&").strip() if title_m else base)
    excerpt_raw = ""
    if intro_m:
        excerpt_raw = re.sub(r"<[^>]+>", "", intro_m.group(1)).replace("&amp;", "&").strip()
    excerpt = (excerpt_raw[:140] if excerpt_raw else f"{title} — 学习笔记。")
    category = _infer_category(title, file)
    return {
        "title": title,
        "date": date_m.group(1) if date_m else today_iso(),
        "category": category,
        "tags": [category],
        "excerpt": excerpt,
        "file": file,
    }


def find_orphan_content(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    registered = {p.get("file") for p in posts}
    orphans: list[dict[str, Any]] = []
    for path in list_content_html_files():
        if path.name in registered:
            continue
        html = path.read_text(encoding="utf-8")
        meta = parse_html_article_meta(html, path.name)
        orphans.append(meta)
    orphans.sort(key=lambda x: str(x.get("date") or ""), reverse=True)
    return orphans


def register_orphan_content(
    posts: list[dict[str, Any]],
    files: list[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    orphans = find_orphan_content(posts)
    if files is not None:
        want = set(files)
        orphans = [o for o in orphans if o["file"] in want]
    if not orphans:
        return posts, []
    next_id = max([int(p.get("id") or 0) for p in posts] + [0]) + 1
    added: list[dict[str, Any]] = []
    next_posts = list(posts)
    for item in orphans:
        post = {
            "id": next_id,
            "title": item["title"],
            "date": item["date"],
            "category": item["category"],
            "tags": item.get("tags") or [item["category"]],
            "excerpt": item["excerpt"],
            "file": item["file"],
        }
        next_id += 1
        next_posts = upsert_post(next_posts, post)
        added.append(post)
    save_posts(next_posts)
    return next_posts, added
