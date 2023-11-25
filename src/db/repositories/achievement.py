from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import Achievement, ReceivedAchievement, User
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

    async def check_user_achievements(
        self, user: User, achievements: Sequence[Achievement]
    ) -> Sequence[Achievement]:
        stmt = (
            select(Achievement)
            .where(Achievement.id.in_([x.id for x in achievements]))
            .join(ReceivedAchievement)
            .where(ReceivedAchievement.user == user)
        )
        return (await self.session.scalars(stmt)).all()
