from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os


def create_app():
    """创建并配置 FastAPI 应用"""
    # 处理直接运行时的导入问题
    if __name__ == "__main__":
        # 将 backend 目录添加到 Python 路径
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from .database import init_db
        from .routers import optimize, history, compare, domains, models as model_routes
        from .utils.exceptions import app_exception_handler, global_exception_handler, AppException
    else:
        from .database import init_db
        from .routers import optimize, history, compare, domains, models as model_routes
        from .utils.exceptions import app_exception_handler, global_exception_handler, AppException
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await init_db()
        yield

    app = FastAPI(
        title="Prompt 智能优化工具",
        description="专业的 Prompt 优化、评分与版本管理平台",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    app.include_router(optimize.router)
    app.include_router(history.router)
    app.include_router(compare.router)
    app.include_router(domains.router)
    app.include_router(model_routes.router)

    @app.get("/")
    async def root():
        return {"message": "Prompt智能优化对比工具 API 服务正在运行", "docs": "/docs"}

    @app.get("/api/health")
    async def health():
        return {"code": 0, "message": "ok"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
