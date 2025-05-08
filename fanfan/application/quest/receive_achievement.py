from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.achievements import (
    AchievementNotFound,
    UserAlreadyHasThisAchievement,
)
from fanfan.core.models.achievement import (
    Achievement,
    AchievementId,
    ReceivedAchievement,
)
from fanfan.core.services.access import UserAccessValidator


class ReceiveAchievement:
    def __init__(
        self,
        achievements_writer: AchievementsRepository,
        access: UserAccessValidator,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ):
        self.achievements_writer = achievements_writer
        self.access = access
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self, achievement_id: AchievementId) -> Achievement:
        async with self.uow:
            user = await self.id_provider.get_current_user()
            self.access.ensure_can_participate_in_quest(user)
            achievement = await self.achievements_writer.get_achievement_by_id(
                achievement_id
            )
            if achievement is None:
                raise AchievementNotFound
            try:
                await self.achievements_writer.add_received_achievement(
                    ReceivedAchievement(achievement_id=achievement_id, user_id=user.id)
                )
                await self.uow.commit()
            except IntegrityError as e:
                await self.uow.rollback()
                raise UserAlreadyHasThisAchievement from e
            else:
                return achievement
