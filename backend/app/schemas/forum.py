from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ForumAuthor(BaseModel):
    id: int
    username: str
    nickname: str


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
    is_pinned: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    author: ForumAuthor | None = None


class ForumThreadDetail(BaseModel):
    id: int
    category_id: int
    category_name: str | None = None
    category_slug: str | None = None
    title: str
    content: str
    reply_count: int
    view_count: int
    is_pinned: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    author: ForumAuthor | None = None
    replies: list["ForumReplyPublic"] = []


class ForumReplyPublic(BaseModel):
    id: int
    thread_id: int
    content: str
    created_at: datetime
    author: ForumAuthor | None = None


class ForumThreadCreate(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)


class ForumThreadUpdate(BaseModel):
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=20000)


class ForumReplyCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class ForumThreadListResponse(BaseModel):
    items: list[ForumThreadListItem]
    total: int
    page: int
    page_size: int


ForumThreadDetail.model_rebuild()
