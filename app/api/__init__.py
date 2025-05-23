from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router
# from app.api.roles import router as roles_router
# from app.api.permissions import router as permissions_router
from app.api.menus import router as menus_router

# 创建API路由
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(auth_router, tags=["认证"])
api_router.include_router(users_router, tags=["用户"])
# api_router.include_router(roles_router, tags=["角色"])
# api_router.include_router(permissions_router, tags=["权限"])
api_router.include_router(menus_router, tags=["菜单"])
