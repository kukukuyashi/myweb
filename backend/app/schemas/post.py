from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PostStatus = Literal["draft", "published"]


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=200)
    content: str = Field(min_length=1)
    category: str = Field(default="未分类", max_length=50)
    tags: list[str] = Field(default_factory=list)
    status: PostStatus = "draft"
    cover_url: str | None = Field(default=None, max_length=512)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = None
    status: PostStatus | None = None
    cover_url: str | None = Field(default=None, max_length=512)


class PostAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str


class PostPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    slug: str
    content: str
    category: str
    tags: list[str]
    status: str
    cover_url: str | None = None
    ai_summary: str | None
    ai_summary_at: datetime | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author: PostAuthor | None = None


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    category: str
    tags: list[str]
    status: str
    cover_url: str | None = None
    ai_summary: str | None
    published_at: datetime | None
    created_at: datetime
    author: PostAuthor | None = None


class PostListResponse(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    page_size: int
