from fastapi import APIRouter

from app.api.v1 import ai, auth, forum, integrations, pomodoro, posts, qa, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(pomodoro.router)
api_router.include_router(forum.router)
api_router.include_router(qa.router)
api_router.include_router(ai.router)
api_router.include_router(integrations.router)
