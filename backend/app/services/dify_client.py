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


def _format_dify_http_error(exc: httpx.HTTPError) -> str:
    if str(exc):
        detail = str(exc)
    elif isinstance(exc, httpx.TimeoutException):
        detail = "请求 Dify 超时，请稍后重试"
    elif isinstance(exc, httpx.ConnectError):
        detail = "无法连接 api.dify.ai，请检查网络"
    else:
        detail = exc.__class__.__name__

    if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
        try:
            body = exc.response.json()
            detail = f"{detail}; dify={body.get('message') or body}"
        except Exception:
            text = (exc.response.text or "").strip()
            if text:
                detail = f"{detail}; body={text[:300]}"
    return detail


def _extract_answer(body: dict) -> str:
    answer = (body.get("answer") or "").strip()
    if not answer:
        return ""
    # DeepSeek 等模型可能返回思考过程，去掉后只保留对用户可见的回答
    think_end = "<" + "/think" + ">"
    for marker in (think_end, "</think>"):
        if marker in answer:
            answer = answer.split(marker, 1)[-1].strip()
    return answer


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


async def run_chat(query: str, user: str, conversation_id: str | None = None) -> dict:
    settings = get_settings()
    if not settings.dify_api_url or not settings.dify_chat_api_key:
        raise DifyError("Dify Chatflow 未配置，请设置 DIFY_API_URL 与 DIFY_CHAT_API_KEY")

    url = _dify_v1_url(settings.dify_api_url, "chat-messages")
    payload: dict = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "user": user,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        async with httpx.AsyncClient(timeout=settings.dify_timeout_sec) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.dify_chat_api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            body = resp.json()
    except httpx.HTTPError as exc:
        raise DifyError(f"Dify Chat 请求失败: {_format_dify_http_error(exc)}") from exc

    answer = _extract_answer(body)
    if not answer:
        raise DifyError(f"Dify 未返回 answer，原始响应: {str(body)[:300]}")
    return {
        "answer": answer,
        "conversation_id": body.get("conversation_id"),
    }
