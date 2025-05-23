from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.admin import admin_router
from app.api import api_router


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    create_db_and_tables()
    yield
    # 关闭时执行
    pass


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(api_router)
app.include_router(admin_router, prefix=settings.ADMIN_PREFIX)

# 前端入口路由
@app.get("/")
async def index():
    """前端入口"""
    return {"message": "API服务运行正常", "status": "ok"}

# SPA应用入口
@app.get(f"{settings.ADMIN_PREFIX}{{path:path}}")
async def serve_spa(path: str):
    """提供SPA应用"""
    # 返回index.html，由前端路由处理
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="前端应用未构建")