from datetime import datetime

from pydantic import BaseModel

from app.schemas.forum import ForumAuthor


class NotificationItem(BaseModel):
    id: int
    type: str
    is_read: bool
    created_at: datetime
    actor: ForumAuthor | None = None
    thread_id: int | None = None
    reply_id: int | None = None
    thread_title: str | None = None


class NotificationListResponse(BaseModel):
    items: list[NotificationItem]
    total: int
    unread: int
    page: int
    page_size: int