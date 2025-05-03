from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import AchievementORM, ReceivedAchievementORM
from fanfan.core.dto.achievement import UserAchievementDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.achievement import (
    Achievement,
    AchievementId,
)
from fanfan.core.models.user import User, UserId


class AchievementsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_user_dto(
        achievement: AchievementORM, received: ReceivedAchievementORM
    ) -> UserAchievementDTO:
        return UserAchievementDTO(
            id=achievement.id,
            title=achievement.title,
            description=achievement.description,
            is_received=bool(received),
        )

    async def get_achievement_by_id(
        self, achievement_id: AchievementId
    ) -> Achievement | None:
        stmt = select(AchievementORM).where(AchievementORM.id == achievement_id)
        achievement_orm = await self.session.scalar(stmt)
        return achievement_orm.to_model() if achievement_orm else None

    async def read_achievements_for_user(
        self, user_id: UserId, pagination: Pagination | None = None
    ) -> list[UserAchievementDTO]:
        stmt = (
            select(AchievementORM, ReceivedAchievementORM)
            .order_by(AchievementORM.order)
            .outerjoin(
                ReceivedAchievementORM,
                and_(
                    ReceivedAchievementORM.achievement_id == AchievementORM.id,
                    ReceivedAchievementORM.user_id == user_id,
                ),
            )
        )

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        results = (await self.session.execute(stmt)).all()

        return [
            self._to_user_dto(achievement_orm, received_orm)
            for achievement_orm, received_orm in results
        ]

    async def count_achievements(self) -> int:
        return await self.session.scalar(select(func.count(AchievementORM.id)))

    async def add_achievement_to_user(
        self,
        achievement: Achievement,
        user: User,
        from_user_id: UserId | None = None,
    ) -> None:
        received_orm = ReceivedAchievementORM(
            achievement_id=achievement.id, user_id=user.id, from_user_id=from_user_id
        )
        self.session.add(received_orm)
        await self.session.flush([received_orm])

    async def delete_all_user_achievements(self, user_id: UserId) -> None:
        await self.session.execute(
            delete(ReceivedAchievementORM).where(
                ReceivedAchievementORM.user_id == user_id
            )
        )
