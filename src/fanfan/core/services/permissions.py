from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.permissions import PermissionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.exceptions.permissions import (
    PermissionNotFound,
    UserAlreadyHasPermission,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.permission import UserPermission
from fanfan.core.vo.permission import (
    PermissionName,
    PermissionObjectId,
    PermissionObjectType,
)
from fanfan.core.vo.user import UserId


class UserPermissionService:
    def __init__(self, perm_repo: PermissionsRepository, user_repo: UsersRepository):
        self.perm_repo = perm_repo
        self.user_repo = user_repo

    async def add_permission(
        self,
        perm_name: PermissionName,
        user_id: UserId,
        object_type: PermissionObjectType | None = None,
        object_id: PermissionObjectId | None = None,
    ) -> UserPermission:
        user = await self.user_repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound
        permission = await self.perm_repo.get_permission_by_name(perm_name)
        if permission is None:
            raise PermissionNotFound
        user_perm = UserPermission(
            permission_id=permission.id,
            user_id=user_id,
            object_type=object_type,
            object_id=object_id,
        )
        try:
            user_perm = await self.perm_repo.add_user_permission(user_perm)
        except IntegrityError as e:
            user_perm = await self.perm_repo.get_user_permission(
                permission_id=permission.id,
                user_id=user_id,
                object_type=object_type,
                object_id=object_id,
            )
            if user_perm:
                raise UserAlreadyHasPermission from e
            raise
        else:
            return user_perm

    async def get_user_permission(
        self,
        perm_name: PermissionName,
        user_id: UserId,
        object_type: PermissionObjectType | None = None,
        object_id: PermissionObjectId | None = None,
    ) -> UserPermission | None:
        user = await self.user_repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound
        permission = await self.perm_repo.get_permission_by_name(perm_name)
        if permission is None:
            raise PermissionNotFound
        return await self.perm_repo.get_user_permission(
            permission_id=permission.id,
            user_id=user_id,
            object_type=object_type,
            object_id=object_id,
        )
