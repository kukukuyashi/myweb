from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.sanitize import sanitize_html


class QaMessageCreate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    content: str = Field(min_length=1, max_length=500)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        return sanitize_html(v)


class QaMessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    content: str
    created_at: datetime
