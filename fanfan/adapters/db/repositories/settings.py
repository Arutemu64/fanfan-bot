from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import GlobalSettings
from fanfan.core.models.settings import GlobalSettingsModel


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self) -> GlobalSettingsModel | None:
        settings = await self.session.get(GlobalSettings, 1)
        return settings.to_model() if settings else None

    async def save_settings(self, model: GlobalSettingsModel):
        await self.session.merge(GlobalSettings.from_model(model))
