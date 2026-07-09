from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QaMessageCreate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    content: str = Field(min_length=1, max_length=500)


class QaMessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    content: str
    created_at: datetime
