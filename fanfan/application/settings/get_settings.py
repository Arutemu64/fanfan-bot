from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.settings import SettingsNotFound
from fanfan.core.models.settings import SettingsDTO
from fanfan.infrastructure.db.models import Settings


class GetSettings:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self) -> SettingsDTO:
        if settings := await self.session.get(Settings, 1):
            return settings.to_dto()
        raise SettingsNotFound
