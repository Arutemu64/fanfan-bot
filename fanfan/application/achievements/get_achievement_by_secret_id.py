from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.achievements import AchievementNotFound
from fanfan.core.models.achievement import AchievementDTO
from fanfan.infrastructure.db.models import Achievement


class GetAchievementBySecretId:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, secret_id: str) -> AchievementDTO:
        achievement = await self.session.scalar(
            select(Achievement).where(Achievement.secret_id == secret_id),
        )
        if achievement:
            return achievement.to_dto()
        raise AchievementNotFound
