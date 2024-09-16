from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.models.user import UserStats
from fanfan.infrastructure.db.models import Achievement, ReceivedAchievement


class GetUserStats:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, user_id: int) -> UserStats:
        received_count_query = (
            select(func.count(ReceivedAchievement.id))
            .where(ReceivedAchievement.user_id == user_id)
            .label("received")
        )
        achievements_count_query = select(func.count(Achievement.id)).label("total")
        query = select(received_count_query, achievements_count_query)
        result = ((await self.session.execute(query)).all())[0]
        return UserStats(
            user_id=user_id,
            achievements_count=result.received,
            total_achievements=result.total,
        )
