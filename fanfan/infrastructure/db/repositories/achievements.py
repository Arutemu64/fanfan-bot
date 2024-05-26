from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.application.dto.achievement import (
    AchievementDTO,
    FullAchievementDTO,
    ReceivedAchievementDTO,
)
from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Achievement, ReceivedAchievement
from fanfan.infrastructure.db.repositories.repo import Repository


class AchievementsRepository(Repository[Achievement]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Achievement, session=session)

    async def add_achievement_to_user(
        self, achievement_id: int, user_id: int
    ) -> ReceivedAchievementDTO:
        received_achievement = ReceivedAchievement(
            user_id=user_id, achievement_id=achievement_id
        )
        self.session.add(received_achievement)
        return received_achievement.to_dto()

    async def get_achievement(self, achievement_id: int) -> Optional[AchievementDTO]:
        achievement = await self.session.get(Achievement, achievement_id)
        return achievement.to_dto() if achievement else None

    async def get_achievement_by_secret_id(
        self, secret_id: str
    ) -> Optional[AchievementDTO]:
        achievement = await self.session.scalar(
            select(Achievement).where(Achievement.secret_id == secret_id).limit(1)
        )
        return achievement.to_dto() if achievement else None

    async def paginate_achievements(
        self,
        page_number: int,
        achievements_per_page: int,
        user_id: Optional[int] = None,
    ) -> Page[FullAchievementDTO]:
        query = select(Achievement).order_by(Achievement.order)
        if user_id:
            query = query.options(contains_eager(Achievement.user_received)).outerjoin(
                ReceivedAchievement,
                and_(
                    ReceivedAchievement.achievement_id == Achievement.id,
                    ReceivedAchievement.user_id == user_id,
                ),
            )
        page = await super()._paginate(query, page_number, achievements_per_page)
        return Page(
            items=[a.to_full_dto() for a in page.items],
            number=page.number,
            total_pages=page.total_pages if page.total_pages > 0 else 1,
        )
