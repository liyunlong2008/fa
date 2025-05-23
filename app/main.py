from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_db_and_tables, engine, get_async_session
from app.core.redis import redis_client
from app.api import api_router
from app.scripts.init_data import init_data
import logging


logger = logging.getLogger(__name__)

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    create_db_and_tables()

    # 初始化数据
    async with get_async_session() as db:
        await init_data(db)

    yield

    # 关闭时执行
    logger.info("应用程序正在关闭，执行清理操作...")

    # 关闭数据库连接池
    try:
        engine.dispose()
        logger.info("数据库连接池已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接池时出错: {e}")

    # 关闭Redis连接
    try:
        redis_client.close()
        logger.info("Redis连接已关闭")
    except Exception as e:
        logger.error(f"关闭Redis连接时出错: {e}")


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