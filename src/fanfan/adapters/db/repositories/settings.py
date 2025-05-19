from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import GlobalSettingsORM
from fanfan.core.models.global_settings import GlobalSettings


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self) -> GlobalSettings | None:
        stmt = select(GlobalSettingsORM).where(GlobalSettingsORM.id == 1)
        settings_orm = await self.session.scalar(stmt)
        return settings_orm.to_model() if settings_orm else None

    async def save_settings(self, settings: GlobalSettings):
        await self.session.merge(GlobalSettingsORM.from_model(settings))
