import logging
from dataclasses import asdict, dataclass, replace

from aiogram.types import User as AiogramUser

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import (
    User,
    UserSettings,
)
from fanfan.core.services.permissions import UserPermissionService
from fanfan.core.vo.telegram import TelegramUserId
from fanfan.core.vo.user import UserRole

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TgAuthenticateDTO:
    tg_id: TelegramUserId
    username: str | None
    first_name: str | None
    last_name: str | None

    @classmethod
    def from_aiogram(cls, user: AiogramUser):
        return TgAuthenticateDTO(
            tg_id=TelegramUserId(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )


class TgAuthenticate:
    def __init__(
        self,
        id_provider: IdProvider,
        users_repo: UsersRepository,
        user_perm_service: UserPermissionService,
        uow: UnitOfWork,
    ):
        self.id_provider = id_provider
        self.users_repo = users_repo
        self.user_perm_service = user_perm_service
        self.uow = uow

    async def __call__(self, data: TgAuthenticateDTO) -> FullUserDTO:
        try:
            user = await self.id_provider.get_current_user()
        except UserNotFound:
            # Create user
            async with self.uow:
                user = User(
                    tg_id=data.tg_id,
                    username=data.username,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    role=UserRole.VISITOR,
                    settings=UserSettings(),
                )
                await self.users_repo.add_user(user)
                await self.uow.commit()
                logger.info("New user %s has registered", user.id, extra={"user": user})
        else:
            # Update details in database
            old_user = replace(user)
            user = replace(user, **asdict(data))
            attrs = ("username", "first_name", "last_name")
            if any(getattr(old_user, a) != getattr(user, a) for a in attrs):
                async with self.uow:
                    await self.users_repo.save_user(user)
                    await self.uow.commit()
        finally:
            user_dto = await self.users_repo.read_user_by_id(user_id=user.id)
        return user_dto
