from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Dict, Any
from app.core.database import get_session
from app.core.auth import get_current_active_user
from app.models.rbac import User
from app.models.menu import Menu, MenuCreate, MenuUpdate, MenuRead
from app.services.menu import MenuService

router = APIRouter()


@router.get("/menus", response_model=List[MenuRead])
async def read_menus(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取菜单列表"""
    menus = await MenuService.get_menus(db, skip, limit)
    return menus


@router.get("/menus/tree", response_model=List[Dict[str, Any]])
async def read_menu_tree(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取完整菜单树"""
    return await MenuService.get_menu_tree(db)


@router.get("/menus/user-tree", response_model=List[Dict[str, Any]])
async def read_user_menu_tree(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的菜单树"""
    return await MenuService.get_user_menu_tree(db, current_user.id)


@router.get("/menus/{menu_id}", response_model=MenuRead)
async def read_menu(
    menu_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取菜单详情"""
    menu = await MenuService.get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    return menu


@router.post("/menus", response_model=MenuRead)
async def create_menu(
    menu: MenuCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建菜单"""
    return await MenuService.create_menu(db, menu)


@router.put("/menus/{menu_id}", response_model=MenuRead)
async def update_menu(
    menu_id: int,
    menu: MenuUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新菜单"""
    db_menu = await MenuService.get_menu_by_id(db, menu_id)
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 更新菜单
    updated_menu = await MenuService.update_menu(db, menu_id, menu)
    return updated_menu


@router.delete("/menus/{menu_id}", response_model=MenuRead)
async def delete_menu(
    menu_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除菜单"""
    db_menu = await MenuService.get_menu_by_id(db, menu_id)
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 删除菜单
    deleted_menu = await MenuService.delete_menu(db, menu_id)
    return deleted_menu
