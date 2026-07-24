from fastapi import APIRouter

from app.api.v1 import acg_bot, admin_stats, ai, anime, auth, checkin, forum, integrations, notes_admin, notifications, pomodoro, posts, qa, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(checkin.router)
api_router.include_router(anime.router)
api_router.include_router(posts.router)
api_router.include_router(pomodoro.router)
api_router.include_router(forum.router)
api_router.include_router(notifications.router)
api_router.include_router(qa.router)
api_router.include_router(ai.router)
api_router.include_router(integrations.router)
api_router.include_router(notes_admin.router)
api_router.include_router(acg_bot.router)
api_router.include_router(admin_stats.router)
