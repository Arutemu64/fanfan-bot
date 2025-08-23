from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import AppSettingsORM
from fanfan.core.models.app_settings import AppSettings


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_settings(self, settings: AppSettings) -> AppSettings:
        settings_orm = AppSettingsORM.from_model(settings)
        self.session.add(settings_orm)
        await self.session.flush([settings_orm])
        return settings_orm.to_model()

    async def get_settings(self) -> AppSettings | None:
        stmt = select(AppSettingsORM).where(AppSettingsORM.id == 1)
        settings_orm = await self.session.scalar(stmt)
        return settings_orm.to_model() if settings_orm else None

    async def save_settings(self, settings: AppSettings):
        await self.session.merge(AppSettingsORM.from_model(settings))
