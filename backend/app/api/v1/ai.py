from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.response import ok
from app.models.user import User
from app.schemas.ai import AiChatRequest, AiSummaryRequest
from app.services.dify_client import DifyError, run_chat, run_summary_workflow

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status", summary="Dify 配置状态")
def ai_status():
    from app.core.config import get_settings

    s = get_settings()
    return ok(
        {
            "summary_ready": bool(s.dify_api_url and s.dify_summary_api_key),
            "chat_ready": bool(s.dify_api_url and s.dify_chat_api_key),
            "dify_api_url": s.dify_api_url or None,
        }
    )


@router.post("/summary", summary="生成文本摘要（Dify Workflow）")
async def ai_summary(payload: AiSummaryRequest, current_user: Annotated[User, Depends(get_current_user)]):
    try:
        outputs = await run_summary_workflow(
            payload.title,
            payload.content,
            user=str(current_user.id),
        )
    except DifyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    summary = outputs.get("summary") or outputs.get("text") or ""
    suggested_tags = outputs.get("suggested_tags")
    return ok(
        {
            "summary": summary,
            "suggested_tags": suggested_tags,
            "raw_outputs": outputs,
        },
        message="摘要生成成功",
    )


@router.post("/chat", summary="站内 AI 助手（Dify Chatflow）")
async def ai_chat(payload: AiChatRequest, current_user: Annotated[User, Depends(get_current_user)]):
    try:
        result = await run_chat(
            payload.query,
            user=str(current_user.id),
            conversation_id=payload.conversation_id,
        )
    except DifyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return ok(result, message="ok")
