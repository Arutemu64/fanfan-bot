import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserId
from fanfan.core.services.access import AccessService
from fanfan.core.utils.notifications import create_points_notification
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AddPointsDTO:
    user_id: UserId
    points: int


class AddPoints(Interactor[AddPointsDTO, None]):
    def __init__(
        self,
        users_repo: UsersRepository,
        uow: UnitOfWork,
        access: AccessService,
        id_provider: IdProvider,
        stream_broker_adapter: StreamBrokerAdapter,
    ) -> None:
        self.users_repo = users_repo
        self.access = access
        self.uow = uow
        self.id_provider = id_provider
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: AddPointsDTO) -> None:
        participant = await self.users_repo.get_user_by_id(data.user_id)
        if participant is None:
            raise UserNotFound
        await self.access.ensure_can_participate_in_quest(participant)
        async with self.uow:
            await self.users_repo.add_points(data.user_id, data.points)
            await self.stream_broker_adapter.send_notification(
                SendNotificationDTO(
                    user_id=data.user_id,
                    notification=create_points_notification(data.points),
                )
            )
            await self.uow.commit()
            logger.info(
                "User %s received %s points from user %s",
                data.user_id,
                data.points,
                self.id_provider.get_current_user_id(),
            )
