import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.settings import SettingsDTO, UpdateSettingsDTO
from fanfan.application.exceptions.settings import SettingsServiceNotFound
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole

logger = logging.getLogger(__name__)


class SettingsService(BaseService):
    async def setup_initial_settings(self) -> None:
        async with self.uow:
            try:
                await self.uow.settings.setup_initial_settings()
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()

    async def get_settings(self) -> SettingsDTO:
        if settings := await self.uow.settings.get_settings():
            return settings
        raise SettingsServiceNotFound

    @check_permission(allowed_roles=[UserRole.ORG])
    async def update_settings(self, dto: UpdateSettingsDTO) -> None:
        async with self.uow:
            await self.uow.settings.update_settings(dto)
            await self.uow.commit()
            logger.info(f"Voting was switched by user id={self.identity.id}")
