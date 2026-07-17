"""Filesystem CRUD for 笔记/*.md with path sandboxing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.services.notes_markdown import (
    COMMON_CATEGORIES,
    parse_frontmatter,
    serialize_note,
    today_iso,
)
from app.services.notes_paths import notes_root

NOTE_FOLDERS = [*COMMON_CATEGORIES, "_drafts"]

SKIP_NOTE_DIRS = {
    "node_modules",
    ".git",
    "typora_plugin",
    "typora_plugin-master",
    "plugin",
    "plugins",
    ".vscode",
    "__pycache__",
    "dist",
    "vendor",
}


def ensure_note_folders() -> Path:
    root = notes_root()
    root.mkdir(parents=True, exist_ok=True)
    for folder in NOTE_FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)
    return root


def _safe_rel(rel_path: str) -> str:
    normalized = rel_path.replace("\\", "/").lstrip("/")
    if not normalized or ".." in normalized.split("/"):
        raise ValueError("非法路径")
    return normalized


def assert_note_abs(rel_path: str) -> Path:
    root = ensure_note_folders().resolve()
    abs_path = (root / _safe_rel(rel_path)).resolve()
    if not str(abs_path).startswith(str(root)):
        raise ValueError("非法路径")
    return abs_path


def category_from_rel_path(rel_path: str) -> str:
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) <= 1:
        return "未分类"
    folder = parts[0]
    if folder == "_drafts":
        return "草稿"
    return folder


def is_draft_path(rel_path: str) -> bool:
    return rel_path.replace("\\", "/").startswith("_drafts/")


def sanitize_file_name(name: str) -> str:
    text = str(name).strip()
    text = re.sub(r'[<>:"/\\|?*]', "-", text)
    text = re.sub(r"\s+", " ", text)
    return text


def should_skip_note_dir(name: str) -> bool:
    return name.startswith(".") or name in SKIP_NOTE_DIRS


def should_skip_note_file(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    base = Path(normalized).name.lower()
    if base == "readme.md":
        return True
    if "typora_plugin" in normalized.lower():
        return True
    if "/plugin/" in f"/{normalized.lower()}/":
        return True
    return False


def walk_markdown_files() -> list[dict[str, Any]]:
    root = ensure_note_folders()
    bucket: list[dict[str, Any]] = []

    def walk(directory: Path) -> None:
        if not directory.is_dir():
            return
        for entry in directory.iterdir():
            if entry.is_dir():
                if should_skip_note_dir(entry.name):
                    continue
                walk(entry)
                continue
            if entry.suffix != ".md":
                continue
            rel = entry.relative_to(root).as_posix()
            if should_skip_note_file(rel):
                continue
            bucket.append({"rel_path": rel, "abs_path": entry, "mtime": entry.stat().st_mtime})

    walk(root)
    return bucket


def list_notes(*, category: str | None = None) -> list[dict[str, Any]]:
    items = []
    for file_info in walk_markdown_files():
        raw = file_info["abs_path"].read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        rel = file_info["rel_path"]
        item = {
            "relPath": rel,
            "folder": category_from_rel_path(rel),
            "isDraft": is_draft_path(rel),
            "mtime": file_info["mtime"],
            "meta": meta,
            "bodyLength": len(body),
        }
        items.append(item)

    if category and category != "全部":
        if category == "草稿":
            items = [i for i in items if i["isDraft"]]
        elif category == "未分类":
            items = [i for i in items if i["folder"] == "未分类"]
        else:
            items = [i for i in items if i["folder"] == category]

    items.sort(key=lambda i: i["mtime"], reverse=True)
    return items


def read_note(rel_path: str) -> dict[str, Any]:
    abs_path = assert_note_abs(rel_path)
    if not abs_path.is_file():
        raise FileNotFoundError("笔记不存在")
    raw = abs_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    return {"relPath": _safe_rel(rel_path), "raw": raw, "meta": meta, "body": body}


def write_note(rel_path: str, *, meta: dict[str, Any], body: str) -> dict[str, Any]:
    abs_path = assert_note_abs(rel_path)
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(serialize_note(meta=meta, body=body), encoding="utf-8")
    return {"relPath": _safe_rel(rel_path), "absPath": str(abs_path)}


def build_markdown_template(
    *,
    title: str,
    date_str: str,
    category: str,
    tags: list[str],
    excerpt: str,
    cover: str | None = None,
) -> str:
    import json

    lines = [
        "---",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"date: {date_str}",
        f"category: {json.dumps(category, ensure_ascii=False)}",
        f"tags: [{', '.join(json.dumps(t, ensure_ascii=False) for t in tags)}]",
        f"excerpt: {json.dumps(excerpt, ensure_ascii=False)}",
    ]
    if cover:
        lines.append(f"cover: {json.dumps(cover, ensure_ascii=False)}")
    lines.extend(["---", "", "## 开头", "", "在这里写正文…", ""])
    return "\n".join(lines)


def create_note(
    *,
    title: str,
    category: str | None = None,
    tags: Any = None,
    excerpt: str | None = None,
    date: str | None = None,
    cover: str | None = None,
    as_draft: bool = False,
) -> dict[str, Any]:
    safe_title = sanitize_file_name(title)
    if not safe_title:
        raise ValueError("标题不能为空")
    folder = "_drafts" if as_draft else (category or "学习")
    rel_path = f"{folder}/{safe_title}.md"
    abs_path = assert_note_abs(rel_path)
    if abs_path.exists():
        raise FileExistsError(f"笔记已存在：{rel_path}")

    if isinstance(tags, list):
        tag_list = [str(t).strip() for t in tags if str(t).strip()]
    else:
        tag_list = [
            t.strip()
            for t in re.split(r"[,，]", str(tags or category or "学习"))
            if t.strip()
        ]
    if not tag_list:
        tag_list = [category or "学习"]

    cat_meta = (category or "学习") if folder == "_drafts" else folder
    content = build_markdown_template(
        title=safe_title,
        date_str=date or today_iso(),
        category=cat_meta,
        tags=tag_list,
        excerpt=excerpt or f"{safe_title} — 学习笔记。",
        cover=cover,
    )
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(content, encoding="utf-8")
    return {"relPath": rel_path, "absPath": str(abs_path)}


def category_to_folder(category_name: str) -> str:
    if category_name == "草稿":
        return "_drafts"
    if category_name == "未分类":
        return ""
    if category_name == "全部":
        raise ValueError("不能移动到「全部」")
    return category_name


def move_note(rel_path: str, target_category: str) -> dict[str, Any]:
    folder = category_to_folder(target_category)
    normalized = _safe_rel(rel_path)
    file_name = Path(normalized).name
    new_rel = f"{folder}/{file_name}" if folder else file_name
    if new_rel == normalized:
        return {"relPath": new_rel, "moved": False}

    src = assert_note_abs(normalized)
    dest = assert_note_abs(new_rel)
    if not src.is_file():
        raise FileNotFoundError("笔记不存在")
    if dest.exists():
        raise FileExistsError(f"目标已存在：{new_rel}")

    note = read_note(normalized)
    meta = dict(note["meta"])
    if folder and folder != "_drafts":
        meta["category"] = target_category
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(serialize_note(meta=meta, body=note["body"]), encoding="utf-8")
    src.unlink()
    return {"relPath": new_rel, "moved": True, "folder": category_from_rel_path(new_rel)}


def delete_note(rel_path: str, *, unpublish: bool = False, posts: list | None = None) -> dict[str, Any]:
    from app.services.posts_catalog import remove_post_by_file, save_posts
    from app.services.notes_paths import content_dir

    normalized = _safe_rel(rel_path)
    abs_path = assert_note_abs(normalized)
    if not abs_path.is_file():
        raise FileNotFoundError("笔记不存在")

    removed_post = False
    removed_html = False
    html_file = ""
    posts = list(posts or [])

    if unpublish:
        raw = abs_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        preview = resolve_post_meta(meta=meta, body=body, md_path=abs_path, posts=posts)
        html_file = preview["file"]
        posts, removed_post = remove_post_by_file(posts, html_file)
        if removed_post:
            save_posts(posts)
        html_path = content_dir() / html_file
        if html_path.is_file():
            html_path.unlink()
            removed_html = True

    abs_path.unlink()
    return {"ok": True, "removedPost": removed_post, "removedHtml": removed_html, "htmlFile": html_file}


def _normalize_match_key(name: str) -> str:
    return re.sub(r"\.(html|md)$", "", str(name), flags=re.I).replace(" ", "").lower()


def find_posts_without_notes(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from app.services.notes_publish import resolve_post_meta

    covered: set[str] = set()
    for note in list_notes():
        try:
            note_data = read_note(note["relPath"])
            resolved = resolve_post_meta(
                meta=note_data["meta"],
                body=note_data["body"],
                md_path=assert_note_abs(note["relPath"]),
                posts=posts,
            )
            for value in [
                resolved.get("file"),
                Path(note["relPath"]).name,
                note_data["meta"].get("title"),
                resolved.get("title"),
                note_data["meta"].get("file"),
            ]:
                if value:
                    covered.add(_normalize_match_key(str(value)))
        except Exception:
            continue

    missing = []
    for post in posts:
        keys = [
            _normalize_match_key(str(post.get("file") or "")),
            _normalize_match_key(str(post.get("title") or "")),
        ]
        if not any(k in covered for k in keys if k):
            missing.append(post)
    missing.sort(key=lambda p: str(p.get("date") or ""), reverse=True)
    return missing


def list_site_only_notes(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "relPath": f"__site__/{post['file']}",
            "folder": "站点文章",
            "isDraft": False,
            "title": post.get("title"),
            "date": post.get("date"),
            "category": post.get("category"),
            "tags": post.get("tags") or [],
            "excerpt": post.get("excerpt") or "",
            "mtime": 0,
            "status": "published",
            "postId": post.get("id"),
            "htmlFile": post.get("file"),
            "siteOnly": True,
        }
        for post in find_posts_without_notes(posts)
    ]


def list_categories(posts: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    posts = posts or []
    notes = list_notes()
    site_only = list_site_only_notes(posts) if posts else []
    site_only_count = len(site_only)
    counts: dict[str, int] = {
        "全部": len(notes) + site_only_count,
        "草稿": 0,
        "未分类": 0,
        "站点文章": site_only_count,
    }
    for cat in COMMON_CATEGORIES:
        counts[cat] = 0
    for note in notes:
        if note["isDraft"]:
            counts["草稿"] = counts.get("草稿", 0) + 1
            continue
        key = "未分类" if note["folder"] == "未分类" else note["folder"]
        counts[key] = counts.get(key, 0) + 1

    dynamic = sorted(
        [
            name
            for name in counts
            if name not in ("全部", "草稿", "未分类", "站点文章") and name not in COMMON_CATEGORIES
        ],
        key=lambda s: s,
    )
    order = ["全部", *COMMON_CATEGORIES, *dynamic, "站点文章", "草稿", "未分类"]
    result = []
    for name in order:
        if name not in counts:
            continue
        count = counts[name]
        if (
            name == "全部"
            or name == "站点文章"
            or count > 0
            or name in COMMON_CATEGORIES
        ):
            result.append({"name": name, "count": count})
    return result


def enrich_notes(posts: list[dict[str, Any]], notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from app.services.notes_publish import get_note_publish_status

    enriched = []
    for note in notes:
        publish = get_note_publish_status(note["relPath"], posts)
        title = note["meta"].get("title") or Path(note["relPath"]).stem
        enriched.append(
            {
                "relPath": note["relPath"],
                "folder": note["folder"],
                "isDraft": note["isDraft"],
                "title": title,
                "date": note["meta"].get("date") or "",
                "category": note["meta"].get("category") or note["folder"],
                "tags": note["meta"].get("tags") or [],
                "excerpt": note["meta"].get("excerpt") or "",
                "mtime": note["mtime"],
                "status": publish["status"],
                "postId": publish["postId"],
                "htmlFile": publish["htmlFile"],
            }
        )
    return enriched
