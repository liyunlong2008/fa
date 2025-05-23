from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from app.core.database import get_session
from app.core.auth import get_current_active_user
from app.models.rbac import User, UserCreate, UserUpdate, UserRead
from app.services.user import UserService

router = APIRouter()


@router.get("/users", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户列表"""
    users = await UserService.get_users(db, skip, limit)
    return users


@router.post("/users", response_model=UserRead)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建用户"""
    # 检查用户名是否已存在
    db_user = await UserService.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    db_user = await UserService.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )

    # 创建用户
    return await UserService.create_user(db, user)


@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户详情"""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return user


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新用户"""
    db_user = await UserService.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新用户
    updated_user = await UserService.update_user(db, user_id, user)
    return updated_user


@router.delete("/users/{user_id}", response_model=UserRead)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除用户"""
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    db_user = await UserService.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 删除用户
    deleted_user = await UserService.delete_user(db, user_id)
    return deleted_user
