import logging

from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.subscriptions import SubscriptionNotFound
from fanfan.core.vo.schedule_event import ScheduleEventId

logger = logging.getLogger(__name__)


class DeleteSubscriptionByEvent:
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(self, event_id: ScheduleEventId) -> None:
        subscription = await self.subscriptions_repo.get_user_subscription_by_event(
            user_id=self.id_provider.get_current_user_id(), event_id=event_id
        )
        if subscription is None:
            raise SubscriptionNotFound
        if subscription.user_id != self.id_provider.get_current_user_id():
            raise AccessDenied
        async with self.uow:
            await self.subscriptions_repo.delete_subscription(subscription)
            await self.uow.commit()
            logger.info(
                "Subscription %s deleted",
                subscription.id,
                extra={"subscription": subscription},
            )
