import logging
from dataclasses import asdict, dataclass, replace

from aiogram.types import User as AiogramUser

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import User, UserData, UserId, UserRole

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AuthenticateDTO:
    id: UserId
    username: str | None
    first_name: str | None
    last_name: str | None

    @classmethod
    def from_aiogram(cls, user: AiogramUser):
        return AuthenticateDTO(
            id=UserId(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )


class Authenticate:
    def __init__(
        self, id_provider: IdProvider, users_repo: UsersRepository, uow: UnitOfWork
    ):
        self.id_provider = id_provider
        self.users_repo = users_repo
        self.uow = uow

    async def __call__(self, data: AuthenticateDTO) -> UserData:
        try:
            user = await self.id_provider.get_current_user()
        except UserNotFound:
            async with self.uow:
                user = User(
                    id=data.id,
                    username=data.username,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    role=UserRole.VISITOR,
                )
                await self.users_repo.add_user(user)
                await self.uow.commit()
                logger.info("New user %s has registered", data.id, extra={"user": user})
                return await self.id_provider.get_current_user()
        else:
            # Update details in database
            old_user = replace(user)
            user = replace(user, **asdict(data))
            if user != old_user:
                async with self.uow:
                    await self.users_repo.save_user(user)
                    await self.uow.commit()
            return user
