from __future__ import annotations

import logging
from dataclasses import dataclass, replace

from adaptix import Retort, name_mapping

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.users import UserNotFound

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class UpdateUserDTO:
    username: str | None = ""  # Cause Telegram username can be removed
    role: UserRole | None = None


class UpdateUser(Interactor[UpdateUserDTO, None]):
    def __init__(
        self, id_provider: IdProvider, uow: UnitOfWork, users_repo: UsersRepository
    ) -> None:
        self.id_provider = id_provider
        self.users_repo = users_repo
        self.uow = uow
        self.retort = Retort(recipe=[name_mapping(omit_default=True)])

    async def __call__(self, data: UpdateUserDTO) -> None:
        user = await self.id_provider.get_current_user()
        if user is None:
            raise UserNotFound
        user = replace(user, **self.retort.dump(data))
        async with self.uow:
            await self.users_repo.update_user(user)
            await self.uow.commit()
            logger.info("User %s was updated", user.id, extra={"user": user})
