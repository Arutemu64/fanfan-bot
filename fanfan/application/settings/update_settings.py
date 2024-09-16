from dataclasses import dataclass

from adaptix import Retort, name_mapping
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.models import Settings


@dataclass
class UpdateSettingsDTO:
    announcement_timeout: int | None = None
    voting_enabled: bool | None = None
    asap_feedback_enabled: bool | None = None


class UpdateSettings:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.retort = Retort(
            recipe=[name_mapping(UpdateSettingsDTO, omit_default=True)]
        )

    async def __call__(self, dto: UpdateSettingsDTO) -> None:
        async with self.session:
            await self.session.execute(
                update(Settings).where(Settings.id == 1).values(self.retort.dump(dto)),
            )
            await self.session.commit()
