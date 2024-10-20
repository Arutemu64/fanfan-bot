import logging
from dataclasses import dataclass, replace

from adaptix import Retort, name_mapping

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserId

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class UpdateUserSettingsDTO:
    user_id: UserId
    items_per_page: int | None = None
    receive_all_announcements: bool | None = None


class UpdateUserSettings(Interactor[UpdateUserSettingsDTO, None]):
    def __init__(self, users_repo: UsersRepository, uow: UnitOfWork):
        self.users_repo = users_repo
        self.uow = uow
        self.retort = Retort(recipe=[name_mapping(omit_default=True)])

    async def __call__(self, dto: UpdateUserSettingsDTO) -> None:
        user = await self.users_repo.get_user_by_id(dto.user_id)
        if user is None:
            raise UserNotFound
        settings = replace(user.settings, **self.retort.dump(dto))
        async with self.uow:
            await self.users_repo.update_user_settings(settings)
            await self.uow.commit()
            logger.info(
                "User %s updated their settings", user.id, extra={"settings": settings}
            )
