from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.adapters.db.models import Achievement, ReceivedAchievement
from fanfan.core.models.achievement import (
    AchievementId,
    AchievementModel,
    FullAchievementModel,
    SecretId,
)
from fanfan.core.models.page import Pagination
from fanfan.core.models.user import UserId


class AchievementsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_achievement_by_id(
        self, achievement_id: AchievementId
    ) -> AchievementModel | None:
        achievement = await self.session.get(Achievement, achievement_id)
        return achievement.to_model() if achievement else None

    async def get_achievement_by_secret_id(
        self, secret_id: SecretId
    ) -> AchievementModel | None:
        achievement = await self.session.scalar(
            select(Achievement).where(Achievement.secret_id == secret_id),
        )
        return achievement.to_model() if achievement else None

    async def list_achievements(
        self, user_id: UserId | None = None, pagination: Pagination | None = None
    ) -> list[FullAchievementModel]:
        query = select(Achievement).order_by(Achievement.order)
        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        if user_id:
            query = query.options(contains_eager(Achievement.user_received)).outerjoin(
                ReceivedAchievement,
                and_(
                    ReceivedAchievement.achievement_id == Achievement.id,
                    ReceivedAchievement.user_id == user_id,
                ),
            )

        achievements = await self.session.scalars(query)

        return [a.to_full_model() for a in achievements]

    async def count_achievements(self) -> int:
        return await self.session.scalar(select(func.count(Achievement.id)))

    async def add_achievement_to_user(
        self, achievement_id: AchievementId, user_id: UserId
    ) -> None:
        received = ReceivedAchievement(achievement_id=achievement_id, user_id=user_id)
        self.session.add(received)
        await self.session.flush([received])
