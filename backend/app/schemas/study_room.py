# -*- coding: utf-8 -*-
"""自习室聊天 Pydantic schema"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator

from app.utils.sanitize import sanitize_html


class StudyRoomMessageCreate(BaseModel):
    content: str | None = Field(default=None, max_length=500)
    sticker_url: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def _check_non_empty(self):
        if not (self.content and self.content.strip()) and not self.sticker_url:
            raise ValueError("content or sticker_url must be provided")
        return self

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return sanitize_html(v)


class StudyRoomMessagePublic(BaseModel):
    id: int
    user_id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    content: str | None = None
    message_type: str = "text"
    sticker_url: str | None = None
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