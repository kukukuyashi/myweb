from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SessionType = Literal["focus", "break"]


class PomodoroSessionCreate(BaseModel):
    duration_sec: int = Field(ge=1, le=7200)
    task_label: str | None = Field(default=None, max_length=200)
    reflection: str | None = Field(default=None, max_length=5000)
    session_type: SessionType = "focus"
    completed_at: datetime | None = None


class PomodoroSessionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    duration_sec: int
    task_label: str | None
    reflection: str | None
    session_type: str
    completed_at: datetime
    created_at: datetime


class PomodoroStats(BaseModel):
    today_minutes: int
    today_sessions: int
    week_minutes: int
    week_sessions: int


class PomodoroSessionListResponse(BaseModel):
    items: list[PomodoroSessionPublic]
    total: int
    page: int
    page_size: int


class PomodoroTimelineDay(BaseModel):
    date: str
    total_minutes: int
    sessions: list[PomodoroSessionPublic]


class PomodoroTimelineResponse(BaseModel):
    days: list[PomodoroTimelineDay]
