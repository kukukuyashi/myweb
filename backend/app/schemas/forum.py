from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ForumAuthor(BaseModel):
    id: int
    username: str
    nickname: str
    level: int = 1
    level_title: str = "见习"


class ForumCategoryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    sort_order: int
    thread_count: int = 0


class ForumThreadListItem(BaseModel):
    id: int
    category_id: int
    category_name: str | None = None
    category_slug: str | None = None
    title: str
    reply_count: int
    view_count: int
    like_count: int = 0
    is_pinned: bool
    is_locked: bool
    is_featured: bool = False
    cover_url: str | None = None
    featured_order: int | None = None
    created_at: datetime
    updated_at: datetime
    author: ForumAuthor | None = None


class ForumReplyPublic(BaseModel):
    id: int
    thread_id: int
    content: str
    like_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    author: ForumAuthor | None = None


class ForumThreadDetail(BaseModel):
    id: int
    category_id: int
    category_name: str | None = None
    category_slug: str | None = None
    title: str
    content: str
    cover_url: str | None = None
    reply_count: int
    view_count: int
    like_count: int = 0
    share_count: int = 0
    is_pinned: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    author: ForumAuthor | None = None
    replies: list[ForumReplyPublic] = []
    liked_by_me: bool = False


class ForumThreadCreate(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)
    cover_url: str | None = Field(default=None, max_length=512)


class ForumThreadUpdate(BaseModel):
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=20000)
    cover_url: str | None = Field(default=None, max_length=512)


class ForumReplyCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class ForumThreadListResponse(BaseModel):
    items: list[ForumThreadListItem]
    total: int
    page: int
    page_size: int


ForumThreadDetail.model_rebuild()
