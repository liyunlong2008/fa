from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from app.utils.timezone import utc_timestamp
from app.models.rbac import Permission


class Menu(SQLModel, table=True):
    """菜单模型"""
    __tablename__ = "menus"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    path: str
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="menus.id", index=True)
    sort_order: int = Field(default=0)
    is_hidden: bool = Field(default=False)
    created_at: int = Field(default_factory=utc_timestamp)
    updated_at: int = Field(default_factory=utc_timestamp)

    # 关系
    permission: Optional[Permission] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class MenuCreate(SQLModel):
    """菜单创建模型"""
    name: str
    path: str
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_hidden: bool = False
    permission_id: Optional[int] = None


class MenuUpdate(SQLModel):
    """菜单更新模型"""
    name: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_hidden: Optional[bool] = None
    permission_id: Optional[int] = None


class MenuRead(SQLModel):
    """菜单读取模型"""
    id: int
    name: str
    path: str
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int
    is_hidden: bool
    permission_id: Optional[int] = None  # 关联的权限ID
    created_at: int
    updated_at: int
