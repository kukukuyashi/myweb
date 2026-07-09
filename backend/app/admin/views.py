from sqladmin import ModelView

from app.models.forum import ForumCategory, ForumReply, ForumThread
from app.models.post import Post
from app.models.qa import QaMessage
from app.models.user import User


class UserAdmin(ModelView, model=User):
    name = "用户"
    name_plural = "用户"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.username, User.email, User.nickname, User.created_at]
    column_searchable_list = [User.username, User.email, User.nickname]
    column_sortable_list = [User.id, User.username, User.created_at]
    column_details_exclude_list = [User.password_hash]
    form_excluded_columns = [User.password_hash, User.created_at, User.updated_at]

    # 用户通过 API 注册；后台只做查看与运维编辑
    can_create = False
    can_delete = True
    can_edit = True
    can_view_details = True


class PostAdmin(ModelView, model=Post):
    name = "文章"
    name_plural = "文章"
    icon = "fa-solid fa-file-lines"

    column_list = [
        Post.id,
        Post.title,
        Post.category,
        Post.status,
        Post.user_id,
        Post.published_at,
        Post.created_at,
    ]
    column_searchable_list = [Post.title, Post.slug, Post.category]
    column_sortable_list = [Post.id, Post.title, Post.published_at, Post.created_at]
    form_columns = [
        Post.user_id,
        Post.title,
        Post.slug,
        Post.content,
        Post.category,
        Post.tags,
        Post.status,
        Post.ai_summary,
        Post.published_at,
    ]

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True


class ForumCategoryAdmin(ModelView, model=ForumCategory):
    name = "论坛板块"
    name_plural = "论坛板块"
    icon = "fa-solid fa-folder"

    column_list = [ForumCategory.id, ForumCategory.name, ForumCategory.slug, ForumCategory.sort_order]
    column_searchable_list = [ForumCategory.name, ForumCategory.slug]
    column_sortable_list = [ForumCategory.id, ForumCategory.sort_order]
    form_columns = [ForumCategory.name, ForumCategory.slug, ForumCategory.description, ForumCategory.sort_order]

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True


class ForumThreadAdmin(ModelView, model=ForumThread):
    name = "论坛帖子"
    name_plural = "论坛帖子"
    icon = "fa-solid fa-comments"

    column_list = [
        ForumThread.id,
        ForumThread.title,
        ForumThread.category_id,
        ForumThread.user_id,
        ForumThread.reply_count,
        ForumThread.view_count,
        ForumThread.is_pinned,
        ForumThread.is_locked,
        ForumThread.created_at,
    ]
    column_searchable_list = [ForumThread.title, ForumThread.content]
    column_sortable_list = [ForumThread.id, ForumThread.created_at, ForumThread.reply_count]
    column_default_sort = [(ForumThread.created_at, True)]
    form_columns = [
        ForumThread.category_id,
        ForumThread.user_id,
        ForumThread.title,
        ForumThread.content,
        ForumThread.is_pinned,
        ForumThread.is_locked,
        ForumThread.reply_count,
        ForumThread.view_count,
    ]

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True


class ForumReplyAdmin(ModelView, model=ForumReply):
    name = "论坛回复"
    name_plural = "论坛回复"
    icon = "fa-solid fa-reply"

    column_list = [
        ForumReply.id,
        ForumReply.thread_id,
        ForumReply.user_id,
        ForumReply.content,
        ForumReply.created_at,
    ]
    column_searchable_list = [ForumReply.content]
    column_sortable_list = [ForumReply.id, ForumReply.created_at]
    column_default_sort = [(ForumReply.created_at, True)]
    form_columns = [ForumReply.thread_id, ForumReply.user_id, ForumReply.content]

    can_create = False
    can_delete = True
    can_edit = True
    can_view_details = True


class QaMessageAdmin(ModelView, model=QaMessage):
    name = "留言板"
    name_plural = "留言板"
    icon = "fa-solid fa-message"

    column_list = [QaMessage.id, QaMessage.name, QaMessage.content, QaMessage.created_at]
    column_searchable_list = [QaMessage.name, QaMessage.content]
    column_sortable_list = [QaMessage.id, QaMessage.created_at]
    column_default_sort = [(QaMessage.created_at, True)]
    form_columns = [QaMessage.name, QaMessage.content]

    can_create = False
    can_delete = True
    can_edit = True
    can_view_details = True
