import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.transactions import TransactionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.events.notifications import NewNotificationEvent
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.transaction import Transaction
from fanfan.core.services.access import UserAccessValidator
from fanfan.core.utils.notifications import create_points_notification
from fanfan.core.vo.user import UserId

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AddPointsToUserDTO:
    user_id: UserId
    points: int
    comment: str


class AddPointsToUser:
    def __init__(
        self,
        users_repo: UsersRepository,
        quest_repo: QuestRepository,
        transactions_repo: TransactionsRepository,
        uow: UnitOfWork,
        access: UserAccessValidator,
        id_provider: IdProvider,
        stream_broker_adapter: EventsBroker,
    ) -> None:
        self.users_repo = users_repo
        self.quest_repo = quest_repo
        self.transactions_repo = transactions_repo
        self.access = access
        self.uow = uow
        self.id_provider = id_provider
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: AddPointsToUserDTO) -> None:
        async with self.uow:
            user = await self.users_repo.get_user_data(data.user_id)
            if user is None:
                raise UserNotFound
            self.access.ensure_can_participate_in_quest(user=user, ticket=user.ticket)
        async with self.uow:
            participant = await self.quest_repo.get_player(user_id=user.id)
            participant.add_points(data.points)
            transaction = Transaction(
                points=data.points,
                comment=data.comment,
                to_user_id=participant.id,
                from_user_id=self.id_provider.get_current_user_id(),
            )

            await self.quest_repo.save_player(participant)
            await self.transactions_repo.add_transaction(transaction)
            await self.uow.commit()

            logger.info(
                "User %s received %s points from user %s",
                data.user_id,
                data.points,
                self.id_provider.get_current_user_id(),
            )
            await self.stream_broker_adapter.publish(
                NewNotificationEvent(
                    user_id=data.user_id,
                    notification=create_points_notification(
                        points=data.points, comment=data.comment
                    ),
                )
            )
