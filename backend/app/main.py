from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from app.admin import setup_admin
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.db import Base, engine
from app.core.response import ok
from app.core.validation_zh import format_validation_errors
from app.models import ForumCategory, ForumReply, ForumThread, PomodoroSession, Post, QaMessage, User  # noqa: F401
from app.models.checkin import UserCheckin  # noqa: F401
from app.models.anime_watchlist import AnimeWatchlist  # noqa: F401
from app.models.acg import AcgSubmission  # noqa: F401
from app.models.xp import ForumReplyLike, ForumThreadLike, ForumThreadShare, UserXpLog  # noqa: F401
from app.services.forum_seed import seed_forum_categories
from app.services.acg_scheduler import shutdown_scheduler, start_scheduler


def _ensure_schema_patches() -> None:
    insp = inspect(engine)
    if insp.has_table("pomodoro_sessions"):
        cols = {c["name"] for c in insp.get_columns("pomodoro_sessions")}
        if "reflection" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE pomodoro_sessions ADD COLUMN reflection TEXT NULL"))
    if insp.has_table("forum_threads"):
        cols = {c["name"] for c in insp.get_columns("forum_threads")}
        with engine.begin() as conn:
            if "is_featured" not in cols:
                conn.execute(text("ALTER TABLE forum_threads ADD COLUMN is_featured TINYINT(1) NOT NULL DEFAULT 0"))
            if "cover_url" not in cols:
                conn.execute(text("ALTER TABLE forum_threads ADD COLUMN cover_url TEXT NULL"))
            if "featured_order" not in cols:
                conn.execute(text("ALTER TABLE forum_threads ADD COLUMN featured_order INT NULL"))
            if "like_count" not in cols:
                conn.execute(text("ALTER TABLE forum_threads ADD COLUMN like_count INT NOT NULL DEFAULT 0"))
            if "share_count" not in cols:
                conn.execute(text("ALTER TABLE forum_threads ADD COLUMN share_count INT NOT NULL DEFAULT 0"))
    if insp.has_table("forum_replies"):
        cols = {c["name"] for c in insp.get_columns("forum_replies")}
        with engine.begin() as conn:
            if "like_count" not in cols:
                conn.execute(text("ALTER TABLE forum_replies ADD COLUMN like_count INT NOT NULL DEFAULT 0"))
    if insp.has_table("users"):
        cols = {c["name"] for c in insp.get_columns("users")}
        with engine.begin() as conn:
            if "xp" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN xp INT NOT NULL DEFAULT 0"))
            if "level" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN level INT NOT NULL DEFAULT 1"))
            if "checkin_streak" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN checkin_streak INT NOT NULL DEFAULT 0"))
            if "last_checkin_date" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_checkin_date DATE NULL"))
    if insp.has_table("posts"):
        cols = {c["name"] for c in insp.get_columns("posts")}
        with engine.begin() as conn:
            if "cover_url" not in cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN cover_url TEXT NULL"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    (Path(settings.upload_dir) / "avatars").mkdir(parents=True, exist_ok=True)
    (Path(settings.upload_dir) / "forum").mkdir(parents=True, exist_ok=True)
    (Path(settings.upload_dir) / "posts").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _ensure_schema_patches()
    seed_forum_categories()
    try:
        from app.core.db import SessionLocal
        from app.services.acg_publish import get_or_create_bot_user

        db = SessionLocal()
        try:
            get_or_create_bot_user(db)
            db.commit()
        finally:
            db.close()
    except Exception:  # noqa: BLE001 - 机器人资料失败不影响主服务
        pass
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="CYINC Platform API",
        description="CYINC 个人全栈平台后端 · FastAPI + MySQL",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    setup_admin(app)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": format_validation_errors(exc)},
        )

    upload_root = Path(settings.upload_dir).resolve()
    upload_root.mkdir(parents=True, exist_ok=True)
    (upload_root / "avatars").mkdir(parents=True, exist_ok=True)
    (upload_root / "forum").mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_root)), name="uploads")

    @app.get("/api/health", tags=["system"], summary="健康检查")
    def health_check():
        return ok({"status": "ok", "service": "cyinc-api"})

    @app.get("/docs", include_in_schema=False)
    def docs_redirect():
        return RedirectResponse(url="/api/docs")

    @app.get("/redoc", include_in_schema=False)
    def redoc_redirect():
        return RedirectResponse(url="/api/redoc")

    return app


app = create_app()
