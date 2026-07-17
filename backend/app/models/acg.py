from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AcgSubmission(Base):
    """ACG 资讯机器人生成的投稿审核队列。

    机器人一键采集当日资讯后写入本表（status=draft），
    人工在管理台预览/编辑后发布，发布时以机器人账号写入 forum_threads。
    """

    __tablename__ = "acg_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON 字符串：各条目的标题 + 真实链接 + 来源，便于审核核对
    source_meta: Mapped[str | None] = mapped_column(Text, nullable=True)
    # draft / published / discarded
    status: Mapped[str] = mapped_column(Text, default="draft", index=True)
    published_thread_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __str__(self) -> str:
        return f"#{self.id} [{self.status}] {(self.title or '')[:40]}"
