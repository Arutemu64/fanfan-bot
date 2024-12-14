from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import DBGlobalSettings
from fanfan.core.models.settings import GlobalSettings


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self) -> GlobalSettings | None:
        settings = await self.session.get(DBGlobalSettings, 1)
        return settings.to_model() if settings else None

    async def save_settings(self, model: GlobalSettings):
        await self.session.merge(DBGlobalSettings.from_model(model))
