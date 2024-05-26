from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.dto.settings import SettingsDTO, UpdateSettingsDTO
from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import Settings


class SettingsRepository(Repository[Settings]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Settings, session=session)

    async def setup_initial_settings(self) -> None:
        settings = Settings(id=1)
        self.session.add(settings)

    async def get_settings(self) -> Optional[SettingsDTO]:
        settings = await self.session.get(Settings, 1)
        return settings.to_dto()

    async def get_announcement_timestamp(self) -> float:
        query = (
            select(Settings.announcement_timestamp)
            .where(Settings.id == 1)
            .limit(1)
            .with_for_update()
        )
        return await self.session.scalar(query)

    async def update_announcement_timestamp(self, timestamp: float) -> None:
        await self.session.execute(
            update(Settings)
            .where(Settings.id == 1)
            .values(announcement_timestamp=timestamp)
        )

    async def update_settings(self, dto: UpdateSettingsDTO) -> None:
        await self.session.execute(
            update(Settings)
            .where(Settings.id == 1)
            .values(**dto.model_dump(exclude_unset=True))
        )
