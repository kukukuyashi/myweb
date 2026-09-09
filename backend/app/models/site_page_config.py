from datetime import datetime

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SitePageConfig(Base):
    __tablename__ = "site_page_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    page_key: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
