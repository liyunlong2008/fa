from sqlmodel import Session, select
from typing import List, Optional, Dict, Any, Set
from app.models.menu import Menu, MenuCreate, MenuUpdate
from app.models.rbac import User, Role, UserRole, Permission, RolePermission
from app.utils.timezone import utc_timestamp


class MenuService:
    """菜单服务类"""

    @staticmethod
    async def get_menus(db: Session, skip: int = 0, limit: int = 100) -> List[Menu]:
        """获取菜单列表"""
        return db.exec(select(Menu).offset(skip).limit(limit)).all()

    @staticmethod
    async def get_menu_by_id(db: Session, menu_id: int) -> Optional[Menu]:
        """通过ID获取菜单"""
        return db.get(Menu, menu_id)

    @staticmethod
    async def get_menu_tree(db: Session) -> List[Dict[str, Any]]:
        """获取完整菜单树"""
        # 获取所有顶级菜单
        root_menus = db.exec(select(Menu).where(Menu.parent_id == None).order_by(Menu.sort_order)).all()

        result = []
        for menu in root_menus:
            menu_dict = MenuService._menu_to_dict(menu)
            # 递归获取子菜单
            menu_dict["children"] = MenuService._get_children(db, menu.id)
            result.append(menu_dict)

        return result

    @staticmethod
    async def get_user_menu_tree(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """根据用户ID获取有权限访问的菜单树"""
        # 获取用户
        user = db.get(User, user_id)
        if not user:
            return []

        # 超级管理员可以访问所有菜单
        if user.is_superuser:
            return await MenuService.get_menu_tree(db)

        # 获取用户的权限代码集合
        permission_codes = await MenuService._get_user_permission_codes(db, user_id)

        # 获取所有顶级菜单
        root_menus = db.exec(select(Menu).where(Menu.parent_id == None).order_by(Menu.sort_order)).all()

        result = []
        for menu in root_menus:
            # 检查菜单是否有权限访问
            menu_dict = MenuService._menu_to_dict(menu)

            # 递归获取有权限的子菜单
            children = MenuService._get_user_children(db, menu.id, permission_codes)

            # 获取菜单关联的权限代码
            menu_permission_code = menu.permission.code if menu.permission else None

            # 如果菜单没有关联权限或者关联权限的代码在用户权限中，或者有可访问的子菜单，则添加到结果中
            if (not menu.permission or
                menu_permission_code in permission_codes or
                children):
                menu_dict["children"] = children
                result.append(menu_dict)

        return result

    @staticmethod
    async def _get_user_permission_codes(db: Session, user_id: int) -> Set[str]:
        """获取用户的所有权限代码"""
        # 获取用户角色
        user_roles = db.exec(
            select(Role)
            .join(UserRole)
            .where(UserRole.user_id == user_id)
        ).all()

        # 获取角色权限
        permission_codes = set()
        for role in user_roles:
            permissions = db.exec(
                select(Permission)
                .join(RolePermission)
                .where(RolePermission.role_id == role.id)
            ).all()

            for permission in permissions:
                permission_codes.add(permission.code)

        return permission_codes

    @staticmethod
    def _menu_to_dict(menu: Menu) -> Dict[str, Any]:
        """将菜单对象转换为字典"""
        return {
            "id": menu.id,
            "name": menu.name,
            "path": menu.path,
            "component": menu.component,
            "redirect": menu.redirect,
            "icon": menu.icon,
            "parent_id": menu.parent_id,
            "sort_order": menu.sort_order,
            "is_hidden": menu.is_hidden,
            "permission_id": menu.permission_id if hasattr(menu, "permission_id") else None,
            "permission_code": menu.permission.code if menu.permission else None,
            "permission_name": menu.permission.name if menu.permission else None,
            "children": []
        }

    @staticmethod
    def _get_children(db: Session, parent_id: int) -> List[Dict[str, Any]]:
        """递归获取所有子菜单"""
        children = db.exec(
            select(Menu).where(Menu.parent_id == parent_id).order_by(Menu.sort_order)
        ).all()

        result = []
        for child in children:
            child_dict = MenuService._menu_to_dict(child)
            child_dict["children"] = MenuService._get_children(db, child.id)
            result.append(child_dict)

        return result

    @staticmethod
    def _get_user_children(db: Session, parent_id: int, permission_codes: Set[str]) -> List[Dict[str, Any]]:
        """递归获取用户有权限的子菜单"""
        children = db.exec(
            select(Menu).where(Menu.parent_id == parent_id).order_by(Menu.sort_order)
        ).all()

        result = []
        for child in children:
            child_dict = MenuService._menu_to_dict(child)

            # 递归获取子菜单
            sub_children = MenuService._get_user_children(db, child.id, permission_codes)

            # 获取菜单关联的权限代码
            child_permission_code = child.permission.code if child.permission else None

            # 如果菜单没有关联权限或者关联权限的代码在用户权限中，或者有可访问的子菜单，则添加到结果中
            if (not child.permission or
                child_permission_code in permission_codes or
                sub_children):
                child_dict["children"] = sub_children
                result.append(child_dict)

        return result

    @staticmethod
    async def create_menu(db: Session, menu: MenuCreate) -> Menu:
        """创建菜单"""
        db_menu = Menu(
            name=menu.name,
            path=menu.path,
            component=menu.component,
            redirect=menu.redirect,
            icon=menu.icon,
            parent_id=menu.parent_id,
            sort_order=menu.sort_order,
            is_hidden=menu.is_hidden,
            permission_id=menu.permission_id
        )

        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)

        return db_menu

    @staticmethod
    async def update_menu(db: Session, menu_id: int, menu: MenuUpdate) -> Optional[Menu]:
        """更新菜单"""
        db_menu = db.get(Menu, menu_id)
        if not db_menu:
            return None

        menu_data = menu.model_dump(exclude_unset=True)

        # 更新时间
        menu_data["updated_at"] = utc_timestamp()

        for key, value in menu_data.items():
            setattr(db_menu, key, value)

        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)

        return db_menu

    @staticmethod
    async def delete_menu(db: Session, menu_id: int) -> Optional[Menu]:
        """删除菜单"""
        db_menu = db.get(Menu, menu_id)
        if not db_menu:
            return None

        # 递归删除子菜单
        children = db.exec(select(Menu).where(Menu.parent_id == menu_id)).all()
        for child in children:
            await MenuService.delete_menu(db, child.id)

        db.delete(db_menu)
        db.commit()

        return db_menu
