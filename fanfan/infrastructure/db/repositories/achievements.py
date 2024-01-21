from typing import Optional, Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.infrastructure.db.models import Achievement, ReceivedAchievement
from fanfan.infrastructure.db.repositories.repo import Repository


class AchievementsRepository(Repository[Achievement]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Achievement, session=session)

    async def get_achievement(self, achievement_id: int) -> Optional[Achievement]:
        return await self.session.get(Achievement, achievement_id)

    async def paginate_achievements(
        self, page: int, achievements_per_page: int, user_id: Optional[int] = None
    ) -> Sequence[Achievement]:
        query = (
            select(Achievement)
            .order_by(Achievement.id)
            .slice(
                start=(page * achievements_per_page),
                stop=(page * achievements_per_page) + achievements_per_page,
            )
        )
        if user_id:
            query = query.options(contains_eager(Achievement.user_received)).outerjoin(
                ReceivedAchievement,
                and_(
                    ReceivedAchievement.achievement_id == Achievement.id,
                    ReceivedAchievement.user_id == user_id,
                ),
            )
        return (await self.session.scalars(query)).all()

    async def count_achievements(self) -> int:
        query = select(func.count(Achievement.id))
        return await self.session.scalar(query)

    async def count_received(self, user_id: int) -> int:
        query = select(func.count(ReceivedAchievement.id)).where(
            ReceivedAchievement.user_id == user_id
        )
        return await self.session.scalar(query)
