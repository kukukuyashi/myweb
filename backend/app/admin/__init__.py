from pathlib import Path

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

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
# 本地备份：部分环境 sqladmin 包内 statics 目录会被锁/装不完整
STATICS_DIR = Path(__file__).resolve().parent / "sqladmin_statics"


def _patch_boolean_widget() -> None:
    """兼容 WTForms 3.2 + 旧版 sqladmin：BooleanInputWidget 缺 validation_attrs 会炸创建页。"""
    try:
        from sqladmin.widgets import BooleanInputWidget

        if not getattr(BooleanInputWidget, "validation_attrs", None):
            BooleanInputWidget.validation_attrs = ["required", "disabled"]
    except Exception:
        pass


def _use_local_statics(app) -> None:
    """若包内 statics 不可用，改挂本地备份目录（供开发机装包失败时兜底）。"""
    if not STATICS_DIR.is_dir():
        return
    statics = StaticFiles(directory=str(STATICS_DIR))
    for route in app.routes:
        if not (isinstance(route, Mount) and route.path == "/admin"):
            continue
        admin_app = route.app
        routes = getattr(admin_app, "routes", None)
        if not routes:
            return
        for i, sub in enumerate(routes):
            if isinstance(sub, Mount) and sub.name == "statics":
                routes[i] = Mount("/statics", app=statics, name="statics")
                return


def setup_admin(app) -> CyAdmin:
    _patch_boolean_widget()
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
    _use_local_statics(app)
    admin.add_view(UserAdmin)
    admin.add_view(PostAdmin)
    admin.add_view(ForumCategoryAdmin)
    admin.add_view(ForumThreadAdmin)
    admin.add_view(ForumReplyAdmin)
    admin.add_view(QaMessageAdmin)
    return admin
