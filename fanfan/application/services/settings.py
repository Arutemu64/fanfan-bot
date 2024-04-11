import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.settings import SettingsDTO
from fanfan.application.exceptions.settings import SettingsServiceNotFound
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import Settings

logger = logging.getLogger(__name__)


class SettingsService(BaseService):
    async def setup_initial_settings(self) -> None:
        async with self.uow:
            try:
                settings = Settings(id=1)
                self.uow.session.add(settings)
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()

    async def get_settings(self) -> SettingsDTO:
        if settings := await self.uow.settings.get_settings():
            return settings.to_dto()
        raise SettingsServiceNotFound

    @check_permission(allowed_roles=[UserRole.ORG])
    async def switch_voting(self, value: bool) -> None:
        async with self.uow:
            settings = await self.uow.settings.get_settings()
            if not settings:
                raise SettingsServiceNotFound
            settings.voting_enabled = value
            await self.uow.commit()
            logger.info(f"Voting was switched by user id={self.identity.id}")
