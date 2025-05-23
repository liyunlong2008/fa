from datetime import timedelta
from app.utils.timezone import utc_now
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from .config import settings
from .database import get_session
from app.models.rbac import User, Role, UserRole, Permission, RolePermission

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.ADMIN_PREFIX}/token")

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

# 生成密码哈希
def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

# 验证用户
async def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """验证用户"""
    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

# 创建访问令牌
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = utc_now() + expires_delta
    else:
        expire = utc_now() + timedelta(minutes=30)  # 默认30分钟
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")  # 使用HS256算法
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

# 获取当前活跃用户
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

# 检查用户是否有特定权限
async def check_permission(user: User, permission_code: str, db: Session) -> bool:
    """检查用户是否有特定权限"""
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True

    # 获取用户角色
    user_roles = db.exec(
        select(Role).join(UserRole).where(UserRole.user_id == user.id)
    ).all()

    # 检查角色是否有权限
    for role in user_roles:
        permissions = db.exec(
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == role.id)
        ).all()

        for perm in permissions:
            if perm.code == permission_code:
                return True

    return False
