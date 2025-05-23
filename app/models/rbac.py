from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.utils.timezone import utc_timestamp


# ==================== 用户模型 ====================
class User(SQLModel, table=True):
    """用户模型"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: int = Field(default_factory=utc_timestamp)
    updated_at: int = Field(default_factory=utc_timestamp)
    
    # 关系
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model="UserRole",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserCreate(SQLModel):
    """用户创建模型"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(SQLModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserRead(SQLModel):
    """用户读取模型"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: int
    updated_at: int


# ==================== 角色模型 ====================
class Role(SQLModel, table=True):
    """角色模型"""
    __tablename__ = "roles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    code: str = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: int = Field(default_factory=utc_timestamp)
    updated_at: int = Field(default_factory=utc_timestamp)
    
    # 关系
    users: List[User] = Relationship(
        back_populates="roles",
        link_model="UserRole",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model="RolePermission",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserRole(SQLModel, table=True):
    """用户角色关联模型"""
    __tablename__ = "user_roles"
    
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
    role_id: Optional[int] = Field(
        default=None, foreign_key="roles.id", primary_key=True
    )


class RoleCreate(SQLModel):
    """角色创建模型"""
    name: str
    code: str
    description: Optional[str] = None


class RoleUpdate(SQLModel):
    """角色更新模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class RoleRead(SQLModel):
    """角色读取模型"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: int
    updated_at: int


# ==================== 权限模型 ====================
class Permission(SQLModel, table=True):
    """权限模型"""
    __tablename__ = "permissions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    code: str = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: int = Field(default_factory=utc_timestamp)
    updated_at: int = Field(default_factory=utc_timestamp)
    
    # 关系
    roles: List[Role] = Relationship(
        back_populates="permissions",
        link_model="RolePermission",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class RolePermission(SQLModel, table=True):
    """角色权限关联模型"""
    __tablename__ = "role_permissions"
    
    role_id: Optional[int] = Field(
        default=None, foreign_key="roles.id", primary_key=True
    )
    permission_id: Optional[int] = Field(
        default=None, foreign_key="permissions.id", primary_key=True
    )


class PermissionCreate(SQLModel):
    """权限创建模型"""
    name: str
    code: str
    description: Optional[str] = None


class PermissionUpdate(SQLModel):
    """权限更新模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class PermissionRead(SQLModel):
    """权限读取模型"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: int
    updated_at: int
