from fastapi import APIRouter

from app.core.config import get_settings
from app.core.response import ok

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/status", summary="第三方集成配置状态")
def integrations_status():
    s = get_settings()
    return ok(
        {
            "dify": {
                "api_url": s.dify_api_url or None,
                "summary_ready": bool(s.dify_api_url and s.dify_summary_api_key),
                "chat_ready": bool(s.dify_api_url and s.dify_chat_api_key),
                "mode": "cloud" if s.dify_api_url and "dify.ai" in s.dify_api_url else "self-hosted",
            },
            "n8n": {
                "webhook_ready": bool(s.n8n_webhook_url),
                "mode": "cloud" if s.n8n_webhook_url and "n8n.cloud" in s.n8n_webhook_url else "self-hosted",
            },
            "redis": {
                "enabled": bool(s.redis_url),
            },
            "docker_required_locally": False,
            "notes": "方案 A：本地无需 Docker，Dify/N8N 使用云服务；Docker 留待 M6 阿里云 ECS。",
        }
    )
