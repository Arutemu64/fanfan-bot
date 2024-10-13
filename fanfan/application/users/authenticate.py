import logging
from dataclasses import dataclass

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import FullUserModel, UserId, UserModel
from fanfan.infrastructure.db.repositories.users import UsersRepository
from fanfan.infrastructure.db.uow import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AuthenticateDTO:
    id: UserId
    username: str | None


class Authenticate(Interactor[AuthenticateDTO, FullUserModel]):
    def __init__(
        self, id_provider: IdProvider, users_repo: UsersRepository, uow: UnitOfWork
    ):
        self.id_provider = id_provider
        self.users_repo = users_repo
        self.uow = uow

    async def __call__(self, data: AuthenticateDTO) -> FullUserModel:
        try:
            return await self.id_provider.get_current_user()
        except UserNotFound:
            async with self.uow:
                user = UserModel(
                    id=data.id, username=data.username, role=UserRole.VISITOR
                )
                await self.users_repo.add_user(user)
                await self.uow.commit()
                logger.info("New user %s has registered", data.id, extra={"user": user})
                return await self.id_provider.get_current_user()
