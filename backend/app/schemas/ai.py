from pydantic import BaseModel, Field, field_validator


class AiSummaryRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class AiChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = Field(
        default=None,
        description="多轮对话 ID；首轮留空。Swagger 请勿使用默认占位符 string。",
    )

    @field_validator("conversation_id", mode="before")
    @classmethod
    def normalize_conversation_id(cls, value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned or cleaned.lower() == "string":
                return None
            return cleaned
        return str(value)
