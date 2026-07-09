import time

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.admin.rate_limit import clear_failures, client_ip, is_locked, lockout_seconds_remaining, record_failure
from app.core.config import get_settings
from app.core.security import verify_password

SESSION_HOURS = 8


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        ip = client_ip(request)
        if is_locked(ip):
            wait = lockout_seconds_remaining(ip)
            # SQLAdmin 只显示登录失败；详细原因写日志即可
            return False

        form = await request.form()
        settings = get_settings()
        username = (form.get("username") or "").strip()
        password = form.get("password") or ""

        if not settings.admin_password_hash:
            return False

        ok = (
            username == settings.admin_username
            and verify_password(password, settings.admin_password_hash)
        )
        if not ok:
            record_failure(ip)
            return False

        clear_failures(ip)
        request.session["admin_authenticated"] = True
        request.session["admin_expires_at"] = time.time() + SESSION_HOURS * 3600
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        if not request.session.get("admin_authenticated"):
            return False
        expires = request.session.get("admin_expires_at", 0)
        if time.time() > expires:
            request.session.clear()
            return False
        return True
