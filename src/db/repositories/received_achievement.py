from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ReceivedAchievement
from .abstract import Repository


class ReceivedAchievementRepo(Repository[ReceivedAchievement]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=ReceivedAchievement, session=session)

    async def new(self, user_id: int, achievement_id: int) -> ReceivedAchievement:
        new_received_achievement = await self.session.merge(
            ReceivedAchievement(user_id=user_id, achievement_id=achievement_id)
        )
        return new_received_achievement

    async def exists(self, user_id: int, achievement_id: int) -> Optional[int]:
        return await super()._exists(
            and_(
                ReceivedAchievement.user_id == user_id,
                ReceivedAchievement.achievement_id == achievement_id,
            )
        )

    async def check(self, user_id: int, achievement_ids: List[int]) -> List[int]:
        stmt = select(ReceivedAchievement.achievement_id).where(
            and_(
                ReceivedAchievement.user_id == user_id,
                ReceivedAchievement.achievement_id.in_(achievement_ids),
            )
        )
        return [a[0] for a in (await self.session.execute(stmt)).all()]
