from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import Settings


class SettingsRepository(Repository[Settings]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Settings, session=session)

    async def get_settings(self) -> Optional[Settings]:
        return await self.session.get(Settings, 1)
