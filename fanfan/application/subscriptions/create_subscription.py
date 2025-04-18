import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.adapters.db.repositories.subscriptions import (
    SubscriptionsRepository,
)
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.schedule import EventNotFound
from fanfan.core.exceptions.subscriptions import SubscriptionAlreadyExist
from fanfan.core.models.event import EventId
from fanfan.core.models.subscription import (
    Subscription,
    SubscriptionFull,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateSubscriptionDTO:
    event_id: EventId
    counter: int


class CreateSubscription:
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
        events_repo: ScheduleRepository,
        uow: UnitOfWork,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.events_repo = events_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(
        self,
        data: CreateSubscriptionDTO,
    ) -> SubscriptionFull:
        async with self.uow:
            try:
                subscription = await self.subscriptions_repo.add_subscription(
                    Subscription(
                        user_id=self.id_provider.get_current_user_id(),
                        event_id=data.event_id,
                        counter=data.counter,
                    )
                )
                await self.uow.commit()
            except IntegrityError as e:
                await self.uow.rollback()
                await self.id_provider.get_current_user()
                if await self.events_repo.get_event_by_id(data.event_id) is None:
                    raise EventNotFound from e
                raise SubscriptionAlreadyExist from e
            else:
                logger.info(
                    "Subscription %s created",
                    subscription.id,
                    extra={"subscription": subscription},
                )
                return await self.subscriptions_repo.get_subscription_by_id(
                    subscription.id
                )
