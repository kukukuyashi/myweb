import httpx

from app.core.config import get_settings


class DifyError(Exception):
    """Dify 未配置或调用失败"""


def _dify_v1_url(api_url: str, path: str) -> str:
    """Accept https://api.dify.ai or .../v1 (Dify 文档两种写法均可)."""
    base = api_url.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]
    return f"{base}/v1/{path.lstrip('/')}"


async def run_summary_workflow(title: str, content: str, user: str = "cyinc-api") -> dict:
    settings = get_settings()
    if not settings.dify_api_url or not settings.dify_summary_api_key:
        raise DifyError("Dify 摘要 Workflow 未配置，请设置 DIFY_API_URL 与 DIFY_SUMMARY_API_KEY")

    url = _dify_v1_url(settings.dify_api_url, "workflows/run")
    payload = {
        "inputs": {"title": title, "content": content},
        "response_mode": "blocking",
        "user": user,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.dify_timeout_sec) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.dify_summary_api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            body = resp.json()
    except httpx.HTTPError as exc:
        raise DifyError(f"Dify Workflow 请求失败: {exc}") from exc

    outputs = body.get("data", {}).get("outputs") or {}
    if not outputs:
        raise DifyError("Dify 未返回 outputs，请检查 Workflow 输出变量名")
    return outputs
