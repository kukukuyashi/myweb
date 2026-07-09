import re
import time
import unicodedata


def slugify(title: str) -> str:
    s = unicodedata.normalize("NFKC", title.strip().lower())
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    if not s:
        s = f"post-{int(time.time())}"
    return s[:180]
