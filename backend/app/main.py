from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from app.admin import setup_admin
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.db import Base, engine
from app.core.response import ok
from app.models import ForumCategory, ForumReply, ForumThread, PomodoroSession, Post, QaMessage, User  # noqa: F401
from app.services.forum_seed import seed_forum_categories


def _ensure_schema_patches() -> None:
    insp = inspect(engine)
    if insp.has_table("pomodoro_sessions"):
        cols = {c["name"] for c in insp.get_columns("pomodoro_sessions")}
        if "reflection" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE pomodoro_sessions ADD COLUMN reflection TEXT NULL"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    (Path(settings.upload_dir) / "avatars").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _ensure_schema_patches()
    seed_forum_categories()
    yield


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

    upload_root = Path(settings.upload_dir).resolve()
    upload_root.mkdir(parents=True, exist_ok=True)
    (upload_root / "avatars").mkdir(parents=True, exist_ok=True)
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
