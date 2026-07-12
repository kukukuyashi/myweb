from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class UserCheckin(Base):
    __tablename__ = "user_checkins"
    __table_args__ = (UniqueConstraint("user_id", "checkin_date", name="uq_user_checkin_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    checkin_date: Mapped[date] = mapped_column(Date, index=True)
    xp_gained: Mapped[int] = mapped_column(Integer, default=0)
    streak_day: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", backref="checkins")
