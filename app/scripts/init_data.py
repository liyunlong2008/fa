from sqlmodel import Session, select
from app.models.rbac import User, Role, Permission, UserRole, RolePermission
from app.core.auth import get_password_hash
from app.utils.timezone import utc_timestamp
import logging

logger = logging.getLogger(__name__)

# 默认超级管理员信息
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",  # 这只是示例，生产环境应使用更强的密码
    "full_name": "超级管理员",
    "is_active": True,
    "is_superuser": True
}

# 默认角色
DEFAULT_ROLES = [
    {
        "name": "超级管理员",
        "code": "superadmin",
        "description": "拥有所有权限的超级管理员"
    },
    {
        "name": "普通用户",
        "code": "user",
        "description": "普通用户，拥有基本权限"
    }
]

# 默认权限
DEFAULT_PERMISSIONS = [
    {
        "name": "用户管理",
        "code": "user:manage",
        "description": "用户的增删改查权限"
    },
    {
        "name": "角色管理",
        "code": "role:manage",
        "description": "角色的增删改查权限"
    },
    {
        "name": "权限管理",
        "code": "permission:manage",
        "description": "权限的增删改查权限"
    },
    {
        "name": "菜单管理",
        "code": "menu:manage",
        "description": "菜单的增删改查权限"
    }
]


async def init_superadmin(db: Session) -> User:
    """初始化超级管理员"""
    # 检查是否已存在超级管理员
    admin = db.exec(
        select(User).where(User.username == DEFAULT_ADMIN["username"])
    ).first()

    if admin:
        logger.info(f"超级管理员 {DEFAULT_ADMIN['username']} 已存在，跳过创建")
        return admin

    # 创建超级管理员
    hashed_password = get_password_hash(DEFAULT_ADMIN["password"])
    admin = User(
        username=DEFAULT_ADMIN["username"],
        email=DEFAULT_ADMIN["email"],
        password=hashed_password,
        full_name=DEFAULT_ADMIN["full_name"],
        is_active=DEFAULT_ADMIN["is_active"],
        is_superuser=DEFAULT_ADMIN["is_superuser"],
        created_at=utc_timestamp(),
        updated_at=utc_timestamp()
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    logger.info(f"超级管理员 {admin.username} 创建成功")
    return admin


async def init_roles(db: Session) -> dict:
    """初始化角色"""
    roles = {}

    for role_data in DEFAULT_ROLES:
        # 检查角色是否已存在
        role = db.exec(
            select(Role).where(Role.code == role_data["code"])
        ).first()

        if not role:
            # 创建角色
            role = Role(
                name=role_data["name"],
                code=role_data["code"],
                description=role_data["description"],
                created_at=utc_timestamp(),
                updated_at=utc_timestamp()
            )

            db.add(role)
            db.commit()
            db.refresh(role)

            logger.info(f"角色 {role.name} 创建成功")
        else:
            logger.info(f"角色 {role.name} 已存在，跳过创建")

        roles[role.code] = role

    return roles


async def init_permissions(db: Session) -> dict:
    """初始化权限"""
    permissions = {}

    for perm_data in DEFAULT_PERMISSIONS:
        # 检查权限是否已存在
        perm = db.exec(
            select(Permission).where(Permission.code == perm_data["code"])
        ).first()

        if not perm:
            # 创建权限
            perm = Permission(
                name=perm_data["name"],
                code=perm_data["code"],
                description=perm_data["description"],
                created_at=utc_timestamp(),
                updated_at=utc_timestamp()
            )

            db.add(perm)
            db.commit()
            db.refresh(perm)

            logger.info(f"权限 {perm.name} 创建成功")
        else:
            logger.info(f"权限 {perm.name} 已存在，跳过创建")

        permissions[perm.code] = perm

    return permissions


async def init_role_permissions(db: Session, roles: dict, permissions: dict) -> None:
    """初始化角色权限关系"""
    # 为超级管理员角色分配所有权限
    superadmin_role = roles.get("superadmin")
    if superadmin_role:
        for perm in permissions.values():
            # 检查角色权限关系是否已存在
            role_perm = db.exec(
                select(RolePermission).where(
                    (RolePermission.role_id == superadmin_role.id) &
                    (RolePermission.permission_id == perm.id)
                )
            ).first()

            if not role_perm:
                # 创建角色权限关系
                role_perm = RolePermission(
                    role_id=superadmin_role.id,
                    permission_id=perm.id
                )

                db.add(role_perm)
                logger.info(f"为角色 {superadmin_role.name} 分配权限 {perm.name}")

        db.commit()

    # 为普通用户角色分配基本权限
    user_role = roles.get("user")
    if user_role:
        # 普通用户只有用户管理权限
        user_perm = permissions.get("user:manage")
        if user_perm:
            # 检查角色权限关系是否已存在
            role_perm = db.exec(
                select(RolePermission).where(
                    (RolePermission.role_id == user_role.id) &
                    (RolePermission.permission_id == user_perm.id)
                )
            ).first()

            if not role_perm:
                # 创建角色权限关系
                role_perm = RolePermission(
                    role_id=user_role.id,
                    permission_id=user_perm.id
                )

                db.add(role_perm)
                db.commit()
                logger.info(f"为角色 {user_role.name} 分配权限 {user_perm.name}")


async def init_user_roles(db: Session, admin: User, roles: dict) -> None:
    """初始化用户角色关系"""
    # 为超级管理员分配超级管理员角色
    superadmin_role = roles.get("superadmin")
    if superadmin_role:
        # 检查用户角色关系是否已存在
        user_role = db.exec(
            select(UserRole).where(
                (UserRole.user_id == admin.id) &
                (UserRole.role_id == superadmin_role.id)
            )
        ).first()

        if not user_role:
            # 创建用户角色关系
            user_role = UserRole(
                user_id=admin.id,
                role_id=superadmin_role.id
            )

            db.add(user_role)
            db.commit()
            logger.info(f"为用户 {admin.username} 分配角色 {superadmin_role.name}")


async def init_data(db: Session) -> None:
    """初始化数据"""
    logger.info("开始初始化数据...")

    # 初始化超级管理员
    admin = await init_superadmin(db)

    # 初始化角色
    roles = await init_roles(db)

    # 初始化权限
    permissions = await init_permissions(db)

    # 初始化角色权限关系
    await init_role_permissions(db, roles, permissions)

    # 初始化用户角色关系
    await init_user_roles(db, admin, roles)

    logger.info("数据初始化完成")