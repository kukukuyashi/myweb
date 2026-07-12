"""Seed demo forum threads for sticker wall preview."""
from app.core.db import SessionLocal
from app.models.forum import ForumCategory, ForumThread
from app.models.user import User
from app.services.forum_seed import seed_forum_categories

BA_COVERS = [
    "/myweb/img/BA/X/星野/d6db50f9097db958e26f0fc42c67eb16.jpeg",
    "/myweb/img/BA/R/日奈/458780fd5ec25ccaefe0fd36ccfbabaa_720.jpg",
    "/myweb/img/BA/mika/acdcfb54cb622b0e8bdf29af195398f6_720.jpg",
    "/myweb/img/BA/A/爱莉/2fd0a12728327701054df80f0686eb0f.jpeg",
    "/myweb/img/BA/魔法伊蕾娜/c9d5e22d00c44a9139f12f3139620173_720.jpg",
    "/myweb/img/BA/C/吹雪/5c10b5b884dbde1fa99b04795a689f57_720.jpg",
    "/myweb/img/BA/G/宫子/07d8a069f0ffec88d536ccf3a067d4d0.png",
]

DEMO_THREADS = [
    ("chat", "碧蓝档案新活动立绘分享", "妃咲这张太绝了，欢迎同好来聊。"),
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
        user = db.query(User).order_by(User.id).first()
        if not user:
            print("No user found — register an account first, then re-run.")
            return
        for i, (slug, title, body) in enumerate(DEMO_THREADS):
            cat = db.query(ForumCategory).filter(ForumCategory.slug == slug).first()
            if not cat:
                continue
            row = db.query(ForumThread).filter(ForumThread.title == title).first()
            cover = BA_COVERS[i] if i < len(BA_COVERS) else None
            order = i + 1
            if row:
                row.is_featured = True
                row.featured_order = order
                if cover and not row.cover_url:
                    row.cover_url = cover
                db.add(row)
                continue
            db.add(
                ForumThread(
                    category_id=cat.id,
                    user_id=user.id,
                    title=title,
                    content=body,
                    reply_count=0,
                    view_count=0,
                    is_featured=True,
                    featured_order=order,
                    cover_url=cover,
                )
            )
        db.commit()
        featured = db.query(ForumThread).filter(ForumThread.is_featured.is_(True)).count()
        print(f"Seeded/updated {len(DEMO_THREADS)} demo threads; featured count: {featured}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_threads()
