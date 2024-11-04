from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import Settings
from fanfan.core.models.settings import SettingsModel


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self) -> SettingsModel | None:
        settings = await self.session.get(Settings, 1)
        return settings.to_model() if settings else None

    async def save_settings(self, model: SettingsModel):
        await self.session.merge(Settings.from_model(model))
