import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.repositories.subscriptions import (
    SubscriptionsRepository,
)
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.subscription import SubscriptionDTO
from fanfan.core.exceptions.schedule import EventNotFound
from fanfan.core.exceptions.subscriptions import SubscriptionAlreadyExist
from fanfan.core.models.subscription import (
    Subscription,
)
from fanfan.core.vo.schedule_event import ScheduleEventId

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateSubscriptionDTO:
    event_id: ScheduleEventId
    counter: int


class CreateSubscription:
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
        schedule_repo: ScheduleEventsRepository,
        uow: UnitOfWork,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.schedule_repo = schedule_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(
        self,
        data: CreateSubscriptionDTO,
    ) -> SubscriptionDTO:
        user_id = self.id_provider.get_current_user_id()
        async with self.uow:
            try:
                subscription = await self.subscriptions_repo.add_subscription(
                    Subscription(
                        user_id=user_id,
                        event_id=data.event_id,
                        counter=data.counter,
                    )
                )
                await self.uow.commit()
            except IntegrityError as e:
                await self.uow.rollback()
                if await self.schedule_repo.read_event_by_id(data.event_id) is None:
                    raise EventNotFound from e
                raise SubscriptionAlreadyExist from e
            else:
                logger.info(
                    "Subscription %s created",
                    subscription.id,
                    extra={"subscription": subscription},
                )
                return await self.subscriptions_repo.read_user_subscription(
                    subscription.id
                )
