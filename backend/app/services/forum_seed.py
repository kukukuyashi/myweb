from app.core.db import SessionLocal
from app.models.forum import ForumCategory

DEFAULT_CATEGORIES = [
    {"name": "技术讨论", "slug": "tech", "description": "编程、架构与工具", "sort_order": 1},
    {"name": "项目展示", "slug": "projects", "description": "作品、Demo 与复盘", "sort_order": 2},
    {"name": "日常交流", "slug": "chat", "description": "闲聊与随想", "sort_order": 3},
    {"name": "ACG每日速报", "slug": "acg-daily", "description": "机器人每日汇总的新番/新闻/二游更新速报", "sort_order": 10},
    {"name": "ACG资讯", "slug": "acg-news", "description": "机器人挑选热门条目展开的图文详细资讯", "sort_order": 11},
]


def seed_forum_categories(db=None) -> None:
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        for item in DEFAULT_CATEGORIES:
            exists = db.query(ForumCategory).filter(ForumCategory.slug == item["slug"]).first()
            if not exists:
                db.add(ForumCategory(**item))
        db.commit()
    finally:
        if own_session:
            db.close()
