from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from sqladmin import Admin


class CyAdmin(Admin):
    """SQLAdmin 中文版：登录错误提示等。"""

    async def login(self, request: Request) -> Response:
        if self.authentication_backend is None:
            from starlette.exceptions import HTTPException

            raise HTTPException(status_code=503, detail="未配置认证后端。")

        context: dict = {}
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "sqladmin/login.html")

        ok = await self.authentication_backend.login(request)
        if not ok:
            context["error"] = "用户名或密码错误，请重试。"
            return await self.templates.TemplateResponse(
                request, "sqladmin/login.html", context, status_code=400
            )

        # 用 path 相对跳转，避免反代场景下 url_for 生成 http:// 把会话弄丢
        return RedirectResponse(url="/admin/", status_code=302)
