from pathlib import Path
import time

from fastapi import HTTPException, UploadFile

from app.core.config import get_settings

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


def guess_image_ext(content_type: str, filename: str | None) -> str | None:
    ext = ALLOWED_IMAGE_TYPES.get(content_type)
    if ext:
        return ext
    if filename:
        suffix = Path(filename).suffix.lower()
        return EXT_BY_SUFFIX.get(suffix)
    return None


async def save_uploaded_image(
    file: UploadFile,
    *,
    subdir: str,
    user_id: int,
    max_bytes: int,
) -> str:
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

    settings = get_settings()
    dest_dir = Path(settings.upload_dir) / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{user_id}_{int(time.time())}{ext}"
    dest = dest_dir / filename
    dest.write_bytes(data)
    return f"/uploads/{subdir}/{filename}"
