from sqlmodel import Session, select
from typing import List, Optional
from app.models.rbac import User, UserCreate, UserUpdate, UserRole
from app.core.auth import get_password_hash
from app.utils.timezone import utc_timestamp


class UserService:
    """用户服务类"""
    
    @staticmethod
    async def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        return db.exec(select(User).offset(skip).limit(limit)).all()
    
    @staticmethod
    async def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return db.get(User, user_id)
    
    @staticmethod
    async def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return db.exec(select(User).where(User.username == username)).first()
    
    @staticmethod
    async def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return db.exec(select(User).where(User.email == email)).first()
    
    @staticmethod
    async def create_user(db: Session, user: UserCreate) -> User:
        """创建用户"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
        """更新用户"""
        db_user = db.get(User, user_id)
        if not db_user:
            return None
        
        user_data = user.model_dump(exclude_unset=True)
        
        # 如果更新密码，需要哈希处理
        if "password" in user_data:
            user_data["password"] = get_password_hash(user_data["password"])
        
        # 更新时间
        user_data["updated_at"] = utc_timestamp()
        
        for key, value in user_data.items():
            setattr(db_user, key, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def delete_user(db: Session, user_id: int) -> Optional[User]:
        """删除用户"""
        db_user = db.get(User, user_id)
        if not db_user:
            return None
        
        # 删除用户角色关联
        user_roles = db.exec(select(UserRole).where(UserRole.user_id == user_id)).all()
        for user_role in user_roles:
            db.delete(user_role)
        
        db.delete(db_user)
        db.commit()
        
        return db_user
    
    @staticmethod
    async def assign_role(db: Session, user_id: int, role_id: int) -> bool:
        """为用户分配角色"""
        # 检查是否已分配
        user_role = db.exec(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        ).first()
        
        if user_role:
            return False
        
        # 分配角色
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        db.commit()
        
        return True
    
    @staticmethod
    async def remove_role(db: Session, user_id: int, role_id: int) -> bool:
        """移除用户的角色"""
        # 检查是否已分配
        user_role = db.exec(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        ).first()
        
        if not user_role:
            return False
        
        # 移除角色
        db.delete(user_role)
        db.commit()
        
        return True
