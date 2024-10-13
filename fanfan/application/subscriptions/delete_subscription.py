import logging

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.subscriptions import SubscriptionNotFound
from fanfan.core.models.subscription import SubscriptionId
from fanfan.infrastructure.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.infrastructure.db.uow import UnitOfWork

logger = logging.getLogger(__name__)


class DeleteSubscription(Interactor[SubscriptionId, None]):
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(self, subscription_id: SubscriptionId) -> None:
        subscription = await self.subscriptions_repo.get_subscription_by_id(
            subscription_id
        )
        if subscription is None:
            raise SubscriptionNotFound
        if subscription.user_id != self.id_provider.get_current_user_id():
            raise AccessDenied
        async with self.uow:
            await self.subscriptions_repo.delete_subscription(subscription_id)
            await self.uow.commit()
            logger.info(
                "Subscription %s deleted",
                subscription.id,
                extra={"subscription": subscription},
            )
