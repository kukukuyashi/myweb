"""Resolve NOTES_ROOT / Content / posts.json for local repo & ECS layouts."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings

# backend/app/services/notes_paths.py → parents[3] = repo root
_REPO_ROOT = Path(__file__).resolve().parents[3]


@lru_cache
def repo_root() -> Path:
    return _REPO_ROOT


@lru_cache
def notes_root() -> Path:
    settings = get_settings()
    if settings.notes_root.strip():
        return Path(settings.notes_root).expanduser().resolve()
    local = (repo_root() / "笔记").resolve()
    ecs = Path("/var/www/cyinc/笔记")
    if local.exists() or not ecs.exists():
        return local
    return ecs.resolve()


@lru_cache
def site_web_root() -> Path:
    """Directory that hosts Content/ and (on ECS) data/posts.json."""
    settings = get_settings()
    if settings.site_web_root.strip():
        return Path(settings.site_web_root).expanduser().resolve()
    ecs = Path("/var/www/cyinc/myweb")
    if (ecs / "Content").is_dir() and not (repo_root() / "public").is_dir():
        return ecs.resolve()
    if (ecs / "Content").is_dir() and (repo_root() / "Content").is_dir():
        # Both exist (code checked out under /var/www/cyinc): prefer live site tree
        return ecs.resolve()
    return repo_root()


@lru_cache
def content_dir() -> Path:
    root = site_web_root()
    if root == repo_root():
        return (root / "Content").resolve()
    return (root / "Content").resolve()


@lru_cache
def posts_json_path() -> Path:
    root = site_web_root()
    if root == repo_root():
        return (root / "public" / "data" / "posts.json").resolve()
    return (root / "data" / "posts.json").resolve()


def clear_path_cache() -> None:
    notes_root.cache_clear()
    site_web_root.cache_clear()
    content_dir.cache_clear()
    posts_json_path.cache_clear()
    repo_root.cache_clear()
