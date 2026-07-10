"""将 FastAPI / Pydantic 校验错误转为中文提示。"""

from __future__ import annotations

from fastapi.exceptions import RequestValidationError

FIELD_LABELS: dict[str, str] = {
    "email": "邮箱",
    "username": "账号",
    "password": "密码",
    "current_password": "当前密码",
    "new_password": "新密码",
    "code": "验证码",
    "nickname": "昵称",
}


def _field_label(err: dict) -> str:
    loc = err.get("loc") or ()
    if not loc:
        return "请求参数"
    key = str(loc[-1])
    return FIELD_LABELS.get(key, key)


def validation_error_to_zh(err: dict) -> str:
    label = _field_label(err)
    msg: str = err.get("msg") or ""
    err_type: str = err.get("type") or ""
    lowered = msg.lower()

    if msg.startswith("Value error, "):
        return msg.removeprefix("Value error, ")

    if err_type == "missing":
        return f"请填写{label}"

    if label == "邮箱" or "email" in lowered or field_is(err, "email"):
        if "@" in msg or "at-sign" in lowered or "email address" in lowered:
            return "邮箱格式不正确，须为有效邮箱地址（含 @ 符号）"
        return "邮箱格式不正确"

    if field_is(err, "code"):
        return "验证码须为 6 位数字"

    if field_is(err, "username"):
        if "pattern" in err_type:
            return "账号仅允许字母、数字与下划线（3–50 位）"
        if "too_short" in err_type:
            return "账号至少 3 个字符"

    if field_is(err, "password"):
        if "too_short" in err_type:
            return "密码至少 9 位，且须含大小写字母与数字"
        return "密码格式不符合要求"

    if "too_short" in err_type:
        ctx = err.get("ctx") or {}
        min_len = ctx.get("min_length")
        if min_len:
            return f"{label}长度不能少于 {min_len} 个字符"

    if "too_long" in err_type:
        ctx = err.get("ctx") or {}
        max_len = ctx.get("max_length")
        if max_len:
            return f"{label}长度不能超过 {max_len} 个字符"

    if "pattern" in err_type:
        return f"{label}格式不正确"

    return f"{label}：{msg}" if msg else f"{label}格式不正确"


def field_is(err: dict, name: str) -> bool:
    loc = err.get("loc") or ()
    return bool(loc) and str(loc[-1]) == name


def format_validation_errors(exc: RequestValidationError) -> str:
    messages = [validation_error_to_zh(e) for e in exc.errors()]
    # 去重并保持顺序
    seen: set[str] = set()
    unique: list[str] = []
    for m in messages:
        if m not in seen:
            seen.add(m)
            unique.append(m)
    return "；".join(unique) if unique else "请求参数有误"
