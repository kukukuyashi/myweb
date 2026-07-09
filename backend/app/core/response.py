from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any = None


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return ApiResponse(code=0, message=message, data=data).model_dump()


def fail(message: str, code: int = 1) -> dict[str, Any]:
    return ApiResponse(code=code, message=message, data=None).model_dump()
