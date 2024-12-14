from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.subscriptions import SubscriptionNotFound
from fanfan.core.models.event import EventId
from fanfan.core.models.subscription import FullSubscription


class GetSubscriptionByEvent(Interactor[EventId, FullSubscription]):
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.id_provider = id_provider

    async def __call__(self, event_id: EventId) -> FullSubscription:
        subscription = await self.subscriptions_repo.get_user_subscription_by_event(
            user_id=self.id_provider.get_current_user_id(), event_id=event_id
        )
        if subscription:
            return subscription
        raise SubscriptionNotFound
