from pathlib import Path
import time

from fastapi import HTTPException, UploadFile

from app.core.config import get_settings
from app.services.cache import cache_available, cache_incr

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/pjpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

EXT_BY_SUFFIX = {
    ".jpg": ".jpg",
    ".jpeg": ".jpg",
    ".png": ".png",
    ".webp": ".webp",
    ".gif": ".gif",
}

# 每个用户在窗口期内最多上传多少张图片（防刷）
UPLOAD_RATE_LIMIT = 20
UPLOAD_RATE_WINDOW = 60  # 秒


def guess_image_ext(content_type: str, filename: str | None) -> str | None:
    ext = ALLOWED_IMAGE_TYPES.get(content_type)
    if ext:
        return ext
    if filename:
        suffix = Path(filename).suffix.lower()
        return EXT_BY_SUFFIX.get(suffix)
    return None


def sniff_image_ext(data: bytes) -> str | None:
    """按文件头魔数判断真实图片类型，防止改后缀伪装非图片文件。"""
    if len(data) < 12:
        return None
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


def check_upload_rate(user_id: int, scope: str = "img") -> None:
    """基于 Redis 的每用户上传频率限制；Redis 不可用时跳过（不阻断本地开发）。"""
    if not cache_available():
        return
    key = f"upload_rate:{scope}:{user_id}"
    count = cache_incr(key, UPLOAD_RATE_WINDOW)
    if count is not None and count > UPLOAD_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="上传过于频繁，请稍后再试")


async def save_uploaded_image(
    file: UploadFile,
    *,
    subdir: str,
    user_id: int,
    max_bytes: int,
) -> str:
    check_upload_rate(user_id, scope=subdir)

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    ext = guess_image_ext(content_type, file.filename)
    if not ext:
        raise HTTPException(status_code=400, detail="仅支持 JPG / PNG / WebP / GIF")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(data) > max_bytes:
        mb = max(1, max_bytes // (1024 * 1024))
        raise HTTPException(status_code=400, detail=f"图片不能超过 {mb}MB")

    # 按真实文件头校验，扩展名/Content-Type 可被伪造
    real_ext = sniff_image_ext(data)
    if not real_ext:
        raise HTTPException(status_code=400, detail="文件不是有效的图片")
    ext = real_ext

    settings = get_settings()
    dest_dir = Path(settings.upload_dir) / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{user_id}_{int(time.time())}{ext}"
    dest = dest_dir / filename
    dest.write_bytes(data)
    return f"/uploads/{subdir}/{filename}"

