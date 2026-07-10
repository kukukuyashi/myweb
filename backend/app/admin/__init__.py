from pathlib import Path

from app.admin.auth import AdminAuth
from app.admin.cyadmin import CyAdmin
from app.admin.views import (
    ForumCategoryAdmin,
    ForumReplyAdmin,
    ForumThreadAdmin,
    PostAdmin,
    QaMessageAdmin,
    UserAdmin,
)
from app.core.config import get_settings
from app.core.db import engine

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def setup_admin(app) -> CyAdmin:
    settings = get_settings()
    authentication_backend = AdminAuth(secret_key=settings.secret_key)
    admin = CyAdmin(
        app,
        engine,
        authentication_backend=authentication_backend,
        base_url="/admin",
        title="CYINC 数据管理",
        templates_dir=str(TEMPLATES_DIR),
    )
    admin.add_view(UserAdmin)
    admin.add_view(PostAdmin)
    admin.add_view(ForumCategoryAdmin)
    admin.add_view(ForumThreadAdmin)
    admin.add_view(ForumReplyAdmin)
    admin.add_view(QaMessageAdmin)
    return admin
