from __future__ import annotations

import logging

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserFull, UserId, UserRole

logger = logging.getLogger(__name__)


class UpdateUser:
    def __init__(
        self, id_provider: IdProvider, uow: UnitOfWork, users_repo: UsersRepository
    ) -> None:
        self.id_provider = id_provider
        self.users_repo = users_repo
        self.uow = uow

    async def _get_user(self, user_id: UserId) -> UserFull:
        user = await self.users_repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound
        current_user = await self.id_provider.get_current_user()
        if (user.id != current_user.id) and (current_user.role != UserRole.ORG):
            raise AccessDenied
        return user

    async def change_role(self, user_id: UserId, role: UserRole) -> None:
        user = await self._get_user(user_id)
        async with self.uow:
            user.role = role
            await self.users_repo.save_user(user)
            await self.uow.commit()
