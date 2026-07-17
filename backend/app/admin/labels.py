from app.models.forum import ForumCategory, ForumReply, ForumThread
from app.models.post import Post
from app.models.qa import QaMessage
from app.models.user import User

COMMON = {
    "id": "ID",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "user_id": "用户 ID",
    "content": "内容",
    "title": "标题",
    "name": "名称",
}

USER_LABELS = {
    **COMMON,
    User.id: "ID",
    User.username: "用户名",
    User.email: "邮箱",
    User.password_hash: "密码哈希",
    User.nickname: "昵称",
    User.avatar: "头像",
    User.xp: "经验值",
    User.level: "等级",
    User.checkin_streak: "连续签到",
    User.last_checkin_date: "上次签到",
    User.created_at: "注册时间",
    User.updated_at: "更新时间",
}

POST_LABELS = {
    **COMMON,
    Post.id: "ID",
    Post.user_id: "作者 ID",
    Post.author: "作者",
    Post.title: "标题",
    Post.slug: "链接别名",
    Post.content: "正文",
    Post.category: "分类",
    Post.tags: "标签",
    Post.status: "状态",
    Post.ai_summary: "AI 摘要",
    Post.ai_summary_at: "摘要生成时间",
    Post.cover_url: "封面图 URL",
    Post.published_at: "发布时间",
    Post.created_at: "创建时间",
    Post.updated_at: "更新时间",
}

FORUM_CATEGORY_LABELS = {
    **COMMON,
    ForumCategory.id: "ID",
    ForumCategory.name: "板块名称",
    ForumCategory.slug: "链接别名",
    ForumCategory.description: "描述",
    ForumCategory.sort_order: "排序",
}

FORUM_THREAD_LABELS = {
    **COMMON,
    ForumThread.id: "ID",
    ForumThread.category_id: "板块 ID",
    ForumThread.category: "板块",
    ForumThread.user_id: "作者 ID",
    ForumThread.user: "作者",
    ForumThread.title: "标题",
    ForumThread.content: "正文",
    ForumThread.reply_count: "回复数",
    ForumThread.view_count: "浏览数",
    ForumThread.like_count: "点赞数",
    ForumThread.share_count: "分享数",
    ForumThread.is_pinned: "置顶",
    ForumThread.is_locked: "锁定",
    ForumThread.is_featured: "精选",
    ForumThread.cover_url: "封面图 URL",
    ForumThread.featured_order: "精选排序",
    ForumThread.created_at: "发帖时间",
    ForumThread.updated_at: "更新时间",
}

FORUM_REPLY_LABELS = {
    **COMMON,
    ForumReply.id: "ID",
    ForumReply.thread_id: "帖子 ID",
    ForumReply.thread: "帖子",
    ForumReply.user_id: "用户 ID",
    ForumReply.user: "作者",
    ForumReply.content: "回复内容",
    ForumReply.like_count: "点赞数",
    ForumReply.created_at: "回复时间",
}

QA_LABELS = {
    **COMMON,
    QaMessage.id: "ID",
    QaMessage.name: "昵称",
    QaMessage.content: "留言内容",
    QaMessage.created_at: "留言时间",
}
