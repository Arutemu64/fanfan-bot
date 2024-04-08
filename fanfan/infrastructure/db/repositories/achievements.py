from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Achievement, ReceivedAchievement
from fanfan.infrastructure.db.repositories.repo import Repository


class AchievementsRepository(Repository[Achievement]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Achievement, session=session)

    async def get_achievement(self, achievement_id: int) -> Optional[Achievement]:
        return await self.session.get(Achievement, achievement_id)

    async def get_achievement_by_secret_id(
        self, secret_id: str
    ) -> Optional[Achievement]:
        return await self.session.scalar(
            select(Achievement).where(Achievement.secret_id == secret_id).limit(1)
        )

    async def paginate_achievements(
        self,
        page_number: int,
        achievements_per_page: int,
        user_id: Optional[int] = None,
    ) -> Page[Achievement]:
        query = select(Achievement).order_by(Achievement.id)
        if user_id:
            query = query.options(contains_eager(Achievement.user_received)).outerjoin(
                ReceivedAchievement,
                and_(
                    ReceivedAchievement.achievement_id == Achievement.id,
                    ReceivedAchievement.user_id == user_id,
                ),
            )
        return await super()._paginate(query, page_number, achievements_per_page)
