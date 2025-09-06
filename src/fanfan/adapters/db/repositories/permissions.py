from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import PermissionORM
from fanfan.adapters.db.models.permission import UserPermissionORM
from fanfan.core.models.permission import Permission, UserPermission
from fanfan.core.vo.permission import (
    PermissionId,
    PermissionName,
    PermissionObjectId,
    PermissionObjectType,
)
from fanfan.core.vo.user import UserId


class PermissionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_permission(self, permission: Permission) -> Permission:
        permission_orm = PermissionORM.from_model(permission)
        self.session.add(permission_orm)
        await self.session.flush([permission_orm])
        return permission_orm.to_model()

    async def add_user_permission(self, user_perm: UserPermission) -> UserPermission:
        user_perm_orm = UserPermissionORM.from_model(user_perm)
        self.session.add(user_perm_orm)
        await self.session.flush([user_perm_orm])
        return user_perm_orm.to_model()

    async def get_permission_by_name(self, name: PermissionName) -> Permission | None:
        stmt = select(PermissionORM).where(PermissionORM.name == name)
        permission_orm = await self.session.scalar(stmt)
        return permission_orm.to_model() if permission_orm else None

    async def get_user_permission(
        self,
        permission_id: PermissionId,
        user_id: UserId,
        object_type: PermissionObjectType | None,
        object_id: PermissionObjectId | None,
    ) -> UserPermission | None:
        stmt = select(UserPermissionORM).where(
            and_(
                UserPermissionORM.permission_id == permission_id,
                UserPermissionORM.user_id == user_id,
                UserPermissionORM.object_type == object_type,
                UserPermissionORM.object_id == object_id,
            )
        )
        user_perm_orm = await self.session.scalar(stmt)
        return user_perm_orm.to_model() if user_perm_orm else None
