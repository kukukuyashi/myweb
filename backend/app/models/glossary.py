from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class GlossaryTerm(Base):
    __tablename__ = "glossary_terms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    aliases: Mapped[str | None] = mapped_column(String(512), nullable=True)
    definition: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
