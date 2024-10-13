import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.common.notifier import Notifier
from fanfan.core.exceptions.achievements import (
    AchievementNotFound,
    UserAlreadyHasThisAchievement,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.achievement import AchievementId
from fanfan.core.models.user import UserId
from fanfan.core.services.access import AccessService
from fanfan.core.utils.notifications import create_achievement_notification
from fanfan.infrastructure.db.repositories.achievements import AchievementsRepository
from fanfan.infrastructure.db.repositories.users import UsersRepository
from fanfan.infrastructure.db.uow import UnitOfWork
from fanfan.infrastructure.stream.routes.send_notification import (
    SendNotificationDTO,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AddAchievementDTO:
    achievement_id: AchievementId
    to_user_id: UserId


class AddAchievement(Interactor[AddAchievementDTO, None]):
    def __init__(
        self,
        users_repo: UsersRepository,
        achievements_repo: AchievementsRepository,
        access: AccessService,
        id_provider: IdProvider,
        uow: UnitOfWork,
        notifier: Notifier,
    ) -> None:
        self.achievements_repo = achievements_repo
        self.users_repo = users_repo
        self.access = access
        self.id_provider = id_provider
        self.uow = uow
        self.notifier = notifier

    async def __call__(self, data: AddAchievementDTO) -> None:
        participant = await self.users_repo.get_user_by_id(data.to_user_id)
        if participant is None:
            raise UserNotFound
        await self.access.ensure_can_participate_in_quest(participant)
        achievement = await self.achievements_repo.get_achievement_by_id(
            data.achievement_id
        )
        if achievement is None:
            raise AchievementNotFound
        async with self.uow:
            try:
                await self.achievements_repo.add_achievement_to_user(
                    achievement_id=data.achievement_id,
                    user_id=participant.id,
                )
                await self.uow.commit()
            except IntegrityError as e:
                await self.uow.rollback()
                raise UserAlreadyHasThisAchievement from e
            else:
                await self.notifier.send_notification(
                    SendNotificationDTO(
                        user_id=data.to_user_id,
                        notification=create_achievement_notification(achievement),
                    )
                )
                logger.info(
                    "User %s received achievement %s from user %s",
                    data.to_user_id,
                    data.achievement_id,
                    self.id_provider.get_current_user_id(),
                    extra={"achievement": achievement},
                )
