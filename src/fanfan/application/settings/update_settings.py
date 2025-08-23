import logging

from adaptix import Retort, name_mapping

from fanfan.adapters.db.repositories.app_settings import SettingsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.settings import SettingsNotFound
from fanfan.core.vo.user import UserRole

logger = logging.getLogger(__name__)


class UpdateSettings:
    def __init__(
        self,
        settings_repo: SettingsRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
    ) -> None:
        self.repo = settings_repo
        self.id_provider = id_provider
        self.uow = uow
        self.retort = Retort(recipe=[name_mapping(omit_default=True)])

    async def toggle_voting(self, voting_enabled: bool) -> None:
        user = await self.id_provider.get_user_data()
        if user.role is not UserRole.ORG:
            raise AccessDenied
        settings = await self.repo.get_settings()
        if settings is None:
            raise SettingsNotFound
        settings.voting_enabled = voting_enabled
        async with self.uow:
            await self.repo.save_settings(settings)
            await self.uow.commit()
            logger.info(
                "Voting toggled by user %s",
                self.id_provider.get_current_user_id(),
                extra={"settings": settings},
            )
