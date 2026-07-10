"""Seed demo forum threads for sticker wall preview."""
from app.core.db import SessionLocal
from app.models.forum import ForumCategory, ForumThread
from app.models.user import User
from app.services.forum_seed import seed_forum_categories

DEMO_THREADS = [
    ("tech", "碧蓝档案新活动立绘分享", "妃咲这张太绝了，欢迎同好来聊。"),
    ("tech", "Vue 3 + FastAPI 论坛 MVP 复盘", "JWT、板块 CRUD、Markdown 编辑器踩坑记录。"),
    ("projects", "星野同人图整理（img/BA）", "把收藏夹里的图床路径统一了一下。"),
    ("tech", "番茄钟 v2 圆环计时体验", "专注结束可以写反思，会进时间线。"),
    ("tech", "ECS 单机 Docker 全栈部署笔记", "MySQL 在宿主机、API 在容器里踩的 ufw 坑。"),
    ("chat", "周末 Cosplay 返图（吹雪）", "场照修图修到半夜，先发几张。"),
    ("projects", "主站侧边栏改版 & 论坛 UI 升级", "参考 ACG 社区排版，贴纸墙展示精选帖。"),
]


def seed_demo_threads() -> None:
    seed_forum_categories()
    db = SessionLocal()
    try:
        if db.query(ForumThread).count() >= 7:
            print("Forum threads already exist, skip demo seed.")
            return
        user = db.query(User).order_by(User.id).first()
        if not user:
            print("No user found — register an account first, then re-run.")
            return
        for slug, title, body in DEMO_THREADS:
            cat = db.query(ForumCategory).filter(ForumCategory.slug == slug).first()
            if not cat:
                continue
            exists = db.query(ForumThread).filter(ForumThread.title == title).first()
            if exists:
                continue
            db.add(
                ForumThread(
                    category_id=cat.id,
                    user_id=user.id,
                    title=title,
                    content=body,
                    reply_count=0,
                    view_count=0,
                )
            )
        db.commit()
        print(f"Seeded up to {len(DEMO_THREADS)} demo forum threads.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_threads()
