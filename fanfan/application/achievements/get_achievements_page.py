from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.achievement import UserAchievementDTO
from fanfan.core.models.page import Page, Pagination
from fanfan.infrastructure.db.models import Achievement, ReceivedAchievement


class GetAchievementsPage:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
        for_user_id: int | None = None,
    ) -> Page[UserAchievementDTO]:
        query = select(Achievement).order_by(Achievement.order)
        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        if user_id := for_user_id or self.id_provider.get_current_user_id():
            query = query.options(contains_eager(Achievement.user_received)).outerjoin(
                ReceivedAchievement,
                and_(
                    ReceivedAchievement.achievement_id == Achievement.id,
                    ReceivedAchievement.user_id == user_id,
                ),
            )

        achievements = await self.session.scalars(query)
        total = await self.session.scalar(select(func.count(Achievement.id)))

        return Page(
            items=[a.to_user_dto() for a in achievements],
            total=total,
        )
