from fastapi import APIRouter
from app.admin.auth import router as auth_router

# 创建Admin路由
admin_router = APIRouter()

# 注册子路由
admin_router.include_router(auth_router)
