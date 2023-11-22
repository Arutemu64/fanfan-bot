from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Settings
from .abstract import Repository


class SettingsRepo(Repository[Settings]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Settings, session=session)

    async def new(
        self,
        voting_enabled: bool,
        announcement_timeout: int,
        announcement_timestamp: float,
    ) -> Settings:
        settings = await self.session.merge(
            Settings(
                id=1,
                voting_enabled=voting_enabled,
                announcement_timeout=announcement_timeout,
                announcement_timestamp=announcement_timestamp,
            )
        )
        return settings

    async def get(self):
        return await self.session.get(Settings, 1)
