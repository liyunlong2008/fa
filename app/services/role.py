from sqlmodel import Session, select
from typing import List, Optional
from app.models.rbac import Role, RoleCreate, RoleUpdate, UserRole, RolePermission
from app.utils.timezone import utc_timestamp


class RoleService:
    """角色服务类"""
    
    @staticmethod
    async def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取角色列表"""
        return db.exec(select(Role).offset(skip).limit(limit)).all()
    
    @staticmethod
    async def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        """通过ID获取角色"""
        return db.get(Role, role_id)
    
    @staticmethod
    async def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        """通过名称获取角色"""
        return db.exec(select(Role).where(Role.name == name)).first()
    
    @staticmethod
    async def get_role_by_code(db: Session, code: str) -> Optional[Role]:
        """通过代码获取角色"""
        return db.exec(select(Role).where(Role.code == code)).first()
    
    @staticmethod
    async def create_role(db: Session, role: RoleCreate) -> Role:
        """创建角色"""
        db_role = Role(
            name=role.name,
            code=role.code,
            description=role.description
        )
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        
        return db_role
    
    @staticmethod
    async def update_role(db: Session, role_id: int, role: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        db_role = db.get(Role, role_id)
        if not db_role:
            return None
        
        role_data = role.model_dump(exclude_unset=True)
        
        # 更新时间
        role_data["updated_at"] = utc_timestamp()
        
        for key, value in role_data.items():
            setattr(db_role, key, value)
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        
        return db_role
    
    @staticmethod
    async def delete_role(db: Session, role_id: int) -> Optional[Role]:
        """删除角色"""
        db_role = db.get(Role, role_id)
        if not db_role:
            return None
        
        # 删除角色与用户的关联
        user_roles = db.exec(select(UserRole).where(UserRole.role_id == role_id)).all()
        for user_role in user_roles:
            db.delete(user_role)
        
        # 删除角色与权限的关联
        role_permissions = db.exec(select(RolePermission).where(RolePermission.role_id == role_id)).all()
        for role_permission in role_permissions:
            db.delete(role_permission)
        
        db.delete(db_role)
        db.commit()
        
        return db_role
    
    @staticmethod
    async def assign_permission(db: Session, role_id: int, permission_id: int) -> bool:
        """为角色分配权限"""
        # 检查是否已分配
        role_permission = db.exec(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
        ).first()
        
        if role_permission:
            return False
        
        # 分配权限
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        db.add(role_permission)
        db.commit()
        
        return True
    
    @staticmethod
    async def remove_permission(db: Session, role_id: int, permission_id: int) -> bool:
        """移除角色的权限"""
        # 检查是否已分配
        role_permission = db.exec(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
        ).first()
        
        if not role_permission:
            return False
        
        # 移除权限
        db.delete(role_permission)
        db.commit()
        
        return True
