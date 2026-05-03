from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class LLMException(AppException):
    pass


class DomainNotFoundException(AppException):
    def __init__(self, domain: str):
        super().__init__(404, f"领域策略 '{domain}' 未找到")


class ModelNotAvailableException(AppException):
    def __init__(self, model: str):
        super().__init__(503, f"模型 '{model}' 不可用")


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=200 if exc.code < 500 else exc.code,
        content={"code": exc.code, "data": None, "message": exc.message},
    )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "data": None, "message": f"服务器内部错误: {str(exc)}"},
    )
