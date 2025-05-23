from sqlmodel import Session, select
from typing import List, Optional
from app.models.rbac import Permission, PermissionCreate, PermissionUpdate, RolePermission
from app.utils.timezone import utc_timestamp


class PermissionService:
    """权限服务类"""
    
    @staticmethod
    async def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
        """获取权限列表"""
        return db.exec(select(Permission).offset(skip).limit(limit)).all()
    
    @staticmethod
    async def get_permission_by_id(db: Session, permission_id: int) -> Optional[Permission]:
        """通过ID获取权限"""
        return db.get(Permission, permission_id)
    
    @staticmethod
    async def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
        """通过名称获取权限"""
        return db.exec(select(Permission).where(Permission.name == name)).first()
    
    @staticmethod
    async def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
        """通过代码获取权限"""
        return db.exec(select(Permission).where(Permission.code == code)).first()
    
    @staticmethod
    async def create_permission(db: Session, permission: PermissionCreate) -> Permission:
        """创建权限"""
        db_permission = Permission(
            name=permission.name,
            code=permission.code,
            description=permission.description
        )
        
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        
        return db_permission
    
    @staticmethod
    async def update_permission(db: Session, permission_id: int, permission: PermissionUpdate) -> Optional[Permission]:
        """更新权限"""
        db_permission = db.get(Permission, permission_id)
        if not db_permission:
            return None
        
        permission_data = permission.model_dump(exclude_unset=True)
        
        # 更新时间
        permission_data["updated_at"] = utc_timestamp()
        
        for key, value in permission_data.items():
            setattr(db_permission, key, value)
        
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        
        return db_permission
    
    @staticmethod
    async def delete_permission(db: Session, permission_id: int) -> Optional[Permission]:
        """删除权限"""
        db_permission = db.get(Permission, permission_id)
        if not db_permission:
            return None
        
        # 删除权限与角色的关联
        role_permissions = db.exec(select(RolePermission).where(RolePermission.permission_id == permission_id)).all()
        for role_permission in role_permissions:
            db.delete(role_permission)
        
        db.delete(db_permission)
        db.commit()
        
        return db_permission
