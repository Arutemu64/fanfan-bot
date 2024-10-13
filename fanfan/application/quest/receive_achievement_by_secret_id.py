import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.achievements import (
    AchievementNotFound,
    UserAlreadyHasThisAchievement,
)
from fanfan.core.models.achievement import AchievementModel, SecretId
from fanfan.infrastructure.db.repositories.achievements import AchievementsRepository
from fanfan.infrastructure.db.uow import UnitOfWork

logger = logging.getLogger(__name__)


class ReceiveAchievementBySecretId(Interactor[SecretId, AchievementModel]):
    def __init__(
        self,
        achievements_repo: AchievementsRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
    ) -> None:
        self.achievements_repo = achievements_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(self, secret_id: SecretId) -> AchievementModel:
        user = await self.id_provider.get_current_user()
        achievement = await self.achievements_repo.get_achievement_by_secret_id(
            secret_id
        )
        if achievement is None:
            raise AchievementNotFound
        try:
            await self.achievements_repo.add_achievement_to_user(
                achievement_id=achievement.id, user_id=user.id
            )
            await self.uow.commit()
        except IntegrityError as e:
            raise UserAlreadyHasThisAchievement from e
        else:
            logger.info(
                "User %s received achievements %s",
                self.id_provider.get_current_user_id(),
                achievement.id,
                extra={"achievement": achievement},
            )
            return achievement
