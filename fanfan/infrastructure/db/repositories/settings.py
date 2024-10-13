from adaptix import Retort
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.models.settings import SettingsModel
from fanfan.infrastructure.db.models import Settings


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.retort = Retort()

    async def get_settings(self) -> SettingsModel | None:
        settings = await self.session.get(Settings, 1)
        return settings.to_model() if settings else None

    async def update_settings(self, model: SettingsModel):
        await self.session.merge(Settings(id=1, **self.retort.dump(model)))
