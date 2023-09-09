from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ReceivedAchievement
from .abstract import Repository


class ReceivedAchievementRepo(Repository[ReceivedAchievement]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=ReceivedAchievement, session=session)

    async def new(self, user_id: int, achievement_id: int) -> ReceivedAchievement:
        new_received_achievement = await self.session.merge(
            ReceivedAchievement(user_id=user_id, achievement_id=achievement_id)
        )
        return new_received_achievement

    async def exists(self, user_id: int, achievement_id: int) -> Optional[int]:
        stmt = (
            select(ReceivedAchievement.id)
            .where(
                and_(
                    ReceivedAchievement.user_id == user_id,
                    ReceivedAchievement.achievement_id == achievement_id,
                )
            )
            .limit(1)
        )
        return await self.session.scalar(stmt)
