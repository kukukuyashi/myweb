# -*- coding: utf-8 -*-
"""自习室聊天 Pydantic schema"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class StudyRoomMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)


class StudyRoomMessagePublic(BaseModel):
    id: int
    user_id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudyRoomOnlineUser(BaseModel):
    user_id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None


class StudyRoomOnlineResponse(BaseModel):
    count: int
    recent: list[StudyRoomOnlineUser] = Field(default_factory=list)