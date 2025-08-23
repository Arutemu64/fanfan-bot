from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import PermissionORM
from fanfan.core.models.permission import Permission, PermissionsList


class PermissionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_permission(self, permission: Permission) -> Permission:
        permission_orm = PermissionORM.from_model(permission)
        self.session.add(permission_orm)
        await self.session.flush([permission_orm])
        return permission_orm.to_model()

    async def get_permission_by_name(self, name: PermissionsList) -> Permission | None:
        stmt = select(PermissionORM).where(PermissionORM.name == name)
        permission_orm = await self.session.scalar(stmt)
        return permission_orm.to_model() if permission_orm else None
