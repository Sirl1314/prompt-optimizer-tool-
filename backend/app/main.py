from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import optimize, history, compare, domains, models as model_routes
from .utils.exceptions import app_exception_handler, global_exception_handler, AppException
from contextlib import asynccontextmanager


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


@app.get("/api/health")
async def health():
    return {"code": 0, "message": "ok"}
