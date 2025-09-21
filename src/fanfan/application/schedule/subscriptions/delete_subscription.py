import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.subscriptions import SubscriptionNotFound
from fanfan.core.vo.subscription import SubscriptionId

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class DeleteSubscriptionDTO:
    subscription_id: SubscriptionId


class DeleteSubscription:
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(self, data: DeleteSubscriptionDTO) -> None:
        user = await self.id_provider.get_current_user()
        subscription = await self.subscriptions_repo.get_subscription_by_id(
            subscription_id=data.subscription_id
        )
        if subscription is None:
            raise SubscriptionNotFound
        if subscription.user_id != user.id:
            raise AccessDenied
        async with self.uow:
            await self.subscriptions_repo.delete_subscription(subscription)
            await self.uow.commit()
            logger.info(
                "Subscription %s deleted",
                subscription.id,
                extra={"subscription": subscription},
            )
