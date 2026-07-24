"""Online notes admin API — CRUD + publish for static blog notes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.admin.rate_limit import clear_failures, client_ip, is_locked, record_failure
from app.api.deps import bearer_scheme
from app.core.config import get_settings
from app.core.response import ok
from app.core.security import ALGORITHM, create_notes_admin_token, verify_password
from app.services import notes_store
from app.services.image_upload import save_uploaded_image
from app.services.notes_paths import content_dir, notes_root, posts_json_path
from app.services.notes_publish import get_note_publish_status, preview_markdown, publish_markdown_file, resolve_post_meta
from app.services.posts_catalog import (
    find_orphan_content,
    list_content_html_files,
    load_posts,
    register_orphan_content,
)
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(prefix="/notes-admin", tags=["notes-admin"])


class LoginBody(BaseModel):
    username: str
    password: str


class NoteCreateBody(BaseModel):
    title: str
    category: str | None = "学习"
    tags: list[str] | str | None = None
    excerpt: str | None = None
    date: str | None = None
    cover: str | None = None
    asDraft: bool = False


class NoteSaveBody(BaseModel):
    meta: dict[str, Any] = Field(default_factory=dict)
    body: str = ""


class MoveBody(BaseModel):
    category: str


class PreviewBody(BaseModel):
    meta: dict[str, Any] = Field(default_factory=dict)
    body: str = ""


class SyncBody(BaseModel):
    files: list[str] | None = None


class AdoptBody(BaseModel):
    htmlFile: str | None = None
    file: str | None = None


def require_notes_admin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或 token 无效")
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("typ") != "notes_admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 无效")
        username = payload.get("sub")
        if not username or username != settings.admin_username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 无效")
        return str(username)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 无效") from exc


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status_code=404, detail=str(exc) or "不存在")
    if isinstance(exc, FileExistsError):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, (ValueError, OSError)):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail=str(exc) or "服务器错误")


@router.post("/login", summary="笔记管理台登录（运维账号）")
def login(payload: LoginBody, request: Request):
    ip = client_ip(request)
    if is_locked(ip):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="尝试过多，请稍后再试")

    settings = get_settings()
    if not settings.admin_password_hash:
        raise HTTPException(status_code=503, detail="未配置 ADMIN_PASSWORD_HASH")

    username = payload.username.strip()
    ok_auth = username == settings.admin_username and verify_password(
        payload.password, settings.admin_password_hash
    )
    if not ok_auth:
        record_failure(ip)
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    clear_failures(ip)
    # 单点登录：顺带种下 SQLAdmin 的 session，使数据管理 iframe 免二次登录
    import time as _time

    request.session["admin_authenticated"] = True
    request.session["admin_expires_at"] = _time.time() + 8 * 3600
    token = create_notes_admin_token(username)
    return ok(
        {
            "token": token,
            "token_type": "bearer",
            "expires_in": settings.notes_admin_token_expire_minutes * 60,
            "username": username,
        }
    )


@router.get("/me", summary="当前笔记管理台会话")
def me(username: Annotated[str, Depends(require_notes_admin)]):
    return ok(
        {
            "username": username,
            "notesRoot": str(notes_root()),
            "contentDir": str(content_dir()),
            "postsJson": str(posts_json_path()),
        }
    )


@router.get("/categories")
def categories(_: Annotated[str, Depends(require_notes_admin)]):
    posts = load_posts()
    return ok({"categories": notes_store.list_categories(posts), "folders": str(notes_root())})


@router.post("/uploads/image", summary="上传笔记正文图片")
async def upload_note_image(
    _: Annotated[str, Depends(require_notes_admin)],
    file: UploadFile = File(...),
):
    settings = get_settings()
    url = await save_uploaded_image(
        file,
        subdir="notes",
        user_id=0,
        max_bytes=settings.max_forum_image_bytes,
    )
    return ok({"url": url, "markdown": f"![图片说明]({url})"})


@router.get("/covers")
def covers(_: Annotated[str, Depends(require_notes_admin)]):
    from pathlib import Path

    from app.services.notes_paths import repo_root, site_web_root

    candidates = [
        repo_root() / "img" / "bkm",
        site_web_root() / "img" / "bkm",
        Path("/var/www/cyinc/img/bkm"),
    ]
    covers_list: list[str] = []
    for cover_dir in candidates:
        if cover_dir.is_dir():
            covers_list = sorted(
                f"img/bkm/{p.name}"
                for p in cover_dir.iterdir()
                if p.suffix.lower() in {".jfif", ".jpg", ".jpeg", ".png", ".webp", ".gif"}
            )
            break
    return ok({"covers": covers_list})


@router.get("/content/status")
def content_status(_: Annotated[str, Depends(require_notes_admin)]):
    posts = load_posts()
    orphans = find_orphan_content(posts)
    return ok(
        {
            "totalHtml": len(list_content_html_files()),
            "registered": len(posts),
            "orphans": [
                {
                    "file": o["file"],
                    "title": o["title"],
                    "date": o["date"],
                    "category": o["category"],
                    "excerpt": o["excerpt"],
                }
                for o in orphans
            ],
        }
    )


@router.post("/content/sync")
def content_sync(body: SyncBody, _: Annotated[str, Depends(require_notes_admin)]):
    posts = load_posts()
    next_posts, added = register_orphan_content(posts, body.files)
    return ok({"ok": True, "added": added, "count": len(added), "posts": next_posts})


@router.get("/notes")
def notes_list(
    _: Annotated[str, Depends(require_notes_admin)],
    category: str = Query("全部"),
):
    posts = load_posts()
    if category == "站点文章":
        return ok({"notes": notes_store.list_site_only_notes(posts)})

    notes = notes_store.list_notes(category=category)
    enriched = notes_store.enrich_notes(posts, notes)

    if category == "全部":
        merged = [*notes_store.list_site_only_notes(posts), *enriched]
        merged.sort(
            key=lambda n: (str(n.get("date") or ""), str(n.get("title") or "")),
            reverse=True,
        )
        # Prefer date DESC then title ASC — approximate like JS
        merged.sort(key=lambda n: str(n.get("title") or ""))
        merged.sort(key=lambda n: str(n.get("date") or ""), reverse=True)
        return ok({"notes": merged})

    return ok({"notes": enriched})


@router.post("/notes", status_code=201)
def notes_create(body: NoteCreateBody, _: Annotated[str, Depends(require_notes_admin)]):
    try:
        created = notes_store.create_note(
            title=body.title,
            category=body.category,
            tags=body.tags,
            excerpt=body.excerpt,
            date=body.date,
            cover=body.cover,
            as_draft=body.asDraft,
        )
        return ok({"ok": True, **created})
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/preview")
def preview(body: PreviewBody, _: Annotated[str, Depends(require_notes_admin)]):
    html = preview_markdown(meta=body.meta or {}, body=body.body or "")
    return ok({"html": html})



@router.post("/notes/adopt", summary="认领单篇仅站点文章为可编辑笔记")
def notes_adopt(body: AdoptBody, _: Annotated[str, Depends(require_notes_admin)]):
    html_file = (body.htmlFile or body.file or "").strip()
    if html_file.startswith("__site__/"):
        html_file = html_file[len("__site__/") :]
    posts = load_posts()
    post = next((p for p in posts if p.get("file") == html_file), None)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="站点文章不存在")
    try:
        result = notes_store.adopt_site_note(post, posts)
        return ok({"ok": True, **result})
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/notes/adopt-all", summary="一键认领全部仅站点文章")
def notes_adopt_all(_: Annotated[str, Depends(require_notes_admin)]):
    posts = load_posts()
    try:
        result = notes_store.adopt_all_site_notes(posts)
        return ok({"ok": True, **result})
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get("/notes/{rel_path:path}")
def notes_get(rel_path: str, _: Annotated[str, Depends(require_notes_admin)]):
    posts = load_posts()
    try:
        if rel_path.startswith("__site__/"):
            html_file = rel_path[len("__site__/") :]
            post = next((p for p in posts if p.get("file") == html_file), None)
            if not post:
                raise FileNotFoundError("站点文章不存在")
            return ok(
                {
                    "relPath": rel_path,
                    "raw": "",
                    "meta": {
                        "title": post.get("title"),
                        "date": post.get("date"),
                        "category": post.get("category"),
                        "tags": post.get("tags") or [],
                        "excerpt": post.get("excerpt") or "",
                        "cover": post.get("cover") or "",
                    },
                    "body": "",
                    "status": "published",
                    "postId": post.get("id"),
                    "htmlFile": post.get("file"),
                    "siteOnly": True,
                    "resolved": post,
                }
            )

        note = notes_store.read_note(rel_path)
        publish = get_note_publish_status(rel_path, posts)
        resolved = resolve_post_meta(
            meta=note["meta"],
            body=note["body"],
            md_path=notes_store.assert_note_abs(rel_path),
            posts=posts,
        )
        return ok(
            {
                **note,
                "status": publish["status"],
                "postId": publish["postId"],
                "htmlFile": publish["htmlFile"],
                "resolved": resolved,
            }
        )
    except Exception as exc:
        raise _http_error(exc) from exc


@router.put("/notes/{rel_path:path}")
def notes_put(rel_path: str, body: NoteSaveBody, _: Annotated[str, Depends(require_notes_admin)]):
    posts = load_posts()
    try:
        actual = rel_path
        target_category = (body.meta or {}).get("category")
        if (
            target_category
            and not notes_store.is_draft_path(rel_path)
            and target_category != notes_store.category_from_rel_path(rel_path)
        ):
            move_result = notes_store.move_note(rel_path, str(target_category))
            if move_result.get("moved"):
                actual = move_result["relPath"]

        notes_store.write_note(actual, meta=body.meta or {}, body=body.body or "")
        publish = get_note_publish_status(actual, posts)
        return ok(
            {
                "ok": True,
                "relPath": actual,
                "status": publish["status"],
                "postId": publish["postId"],
            }
        )
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/notes/{rel_path:path}/publish")
def notes_publish(rel_path: str, _: Annotated[str, Depends(require_notes_admin)]):
    try:
        result = publish_markdown_file(rel_path)
        return ok(
            {
                "ok": True,
                "relPath": rel_path,
                "post": result["post"],
                "updated": result["updated"],
            }
        )
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/notes/{rel_path:path}/move")
def notes_move(rel_path: str, body: MoveBody, _: Annotated[str, Depends(require_notes_admin)]):
    try:
        result = notes_store.move_note(rel_path, body.category)
        return ok({"ok": True, **result})
    except Exception as exc:
        raise _http_error(exc) from exc


@router.delete("/notes/{rel_path:path}")
def notes_delete(
    rel_path: str,
    _: Annotated[str, Depends(require_notes_admin)],
    unpublish: int = Query(0),
):
    try:
        posts = load_posts()
        result = notes_store.delete_note(rel_path, unpublish=bool(unpublish), posts=posts)
        return ok(result)
    except Exception as exc:
        raise _http_error(exc) from exc
