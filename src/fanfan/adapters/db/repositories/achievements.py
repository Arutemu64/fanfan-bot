from sqlalchemy import Select, and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import AchievementORM, ReceivedAchievementORM
from fanfan.core.dto.achievement import AchievementUserDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.achievement import (
    Achievement,
    ReceivedAchievement,
)
from fanfan.core.vo.achievements import AchievementId
from fanfan.core.vo.user import UserId


def _select_achievement_user_dto(user_id: UserId) -> Select:
    return (
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


def _parse_achievement_user_dto(
    achievement: AchievementORM, received: ReceivedAchievementORM
) -> AchievementUserDTO:
    return AchievementUserDTO(
        id=achievement.id,
        title=achievement.title,
        description=achievement.description,
        is_received=bool(received),
    )


class AchievementsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_received_achievement(
        self, received_achievement: ReceivedAchievement
    ) -> None:
        received_achievement_orm = ReceivedAchievementORM.from_model(
            received_achievement
        )
        self.session.add(received_achievement_orm)
        await self.session.flush([received_achievement_orm])

    async def get_achievement_by_id(
        self, achievement_id: AchievementId
    ) -> Achievement | None:
        stmt = select(AchievementORM).where(AchievementORM.id == achievement_id)
        achievement_orm = await self.session.scalar(stmt)
        return achievement_orm.to_model() if achievement_orm else None

    async def delete_all_user_achievements(self, user_id: UserId) -> None:
        await self.session.execute(
            delete(ReceivedAchievementORM).where(
                ReceivedAchievementORM.user_id == user_id
            )
        )

    async def list_achievements_for_user(
        self, user_id: UserId, pagination: Pagination | None = None
    ) -> list[AchievementUserDTO]:
        stmt = _select_achievement_user_dto(user_id).order_by(AchievementORM.order)

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        results = (await self.session.execute(stmt)).all()

        return [
            _parse_achievement_user_dto(achievement_orm, received_orm)
            for achievement_orm, received_orm in results
        ]

    async def count_achievements(self) -> int:
        return await self.session.scalar(select(func.count(AchievementORM.id)))
