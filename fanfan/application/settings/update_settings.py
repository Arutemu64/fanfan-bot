import logging
from dataclasses import dataclass, replace

from adaptix import Retort, name_mapping

from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.settings import SettingsNotFound

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class UpdateSettingsDTO:
    announcement_timeout: int | None = None
    voting_enabled: bool | None = None
    asap_feedback_enabled: bool | None = None
    quest_registration_enabled: bool | None = None
    quest_registrations_limit: int | None = None


class UpdateSettings(Interactor[UpdateSettingsDTO, None]):
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

    async def __call__(self, data: UpdateSettingsDTO) -> None:
        user = await self.id_provider.get_current_user()
        if user.role is not UserRole.ORG:
            raise AccessDenied
        settings = await self.repo.get_settings()
        if settings is None:
            raise SettingsNotFound
        settings = replace(settings, **self.retort.dump(data))
        async with self.uow:
            await self.repo.update_settings(settings)
            await self.uow.commit()
            logger.info(
                "Global settings were updated by user %s",
                self.id_provider.get_current_user_id(),
                extra={"settings": settings},
            )
