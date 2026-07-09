from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    duration_sec: Mapped[int] = mapped_column(Integer)
    task_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reflection: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_type: Mapped[str] = mapped_column(String(20), default="focus", index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", backref="pomodoro_sessions")
