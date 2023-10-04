from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import Achievement
from .abstract import Repository


class AchievementRepo(Repository[Achievement]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Achievement, session=session)

    async def get(self, achievement_id: int) -> Optional[Achievement]:
        return await super()._get(ident=achievement_id)

    async def get_count(self) -> int:
        return await super()._get_count()

    async def paginate(
        self,
        page: int,
        achievements_per_page: int,
    ) -> Page[Achievement]:
        return await super()._paginate(
            page=page,
            items_per_page=achievements_per_page,
        )
