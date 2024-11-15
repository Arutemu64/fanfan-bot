import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.achievements import (
    AchievementNotFound,
    UserAlreadyHasThisAchievement,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.achievement import AchievementId
from fanfan.core.models.user import UserId
from fanfan.core.services.access import AccessService
from fanfan.core.utils.notifications import create_achievement_notification
from fanfan.presentation.stream.routes.notifications.send_notification import (
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
        stream_broker_adapter: StreamBrokerAdapter,
    ) -> None:
        self.achievements_repo = achievements_repo
        self.users_repo = users_repo
        self.access = access
        self.id_provider = id_provider
        self.uow = uow
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: AddAchievementDTO) -> None:
        user = await self.users_repo.get_user_by_id(data.to_user_id)
        if user is None:
            raise UserNotFound
        await self.access.ensure_can_participate_in_quest(user)
        achievement = await self.achievements_repo.get_achievement_by_id(
            data.achievement_id
        )
        if achievement is None:
            raise AchievementNotFound

        async with self.uow:
            try:
                await self.achievements_repo.add_achievement_to_user(
                    achievement_id=data.achievement_id,
                    user_id=user.id,
                )
                await self.uow.commit()
            except IntegrityError as e:
                await self.uow.rollback()
                raise UserAlreadyHasThisAchievement from e
            else:
                logger.info(
                    "User %s received achievement %s from user %s",
                    data.to_user_id,
                    data.achievement_id,
                    self.id_provider.get_current_user_id(),
                    extra={"achievement": achievement},
                )
                await self.stream_broker_adapter.send_notification(
                    SendNotificationDTO(
                        user_id=data.to_user_id,
                        notification=create_achievement_notification(achievement),
                    )
                )
