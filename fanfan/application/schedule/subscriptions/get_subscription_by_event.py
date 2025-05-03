from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.subscriptions import SubscriptionNotFound
from fanfan.core.models.schedule_event import ScheduleEventId
from fanfan.core.models.subscription import SubscriptionFull


class GetSubscriptionByEvent:
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.id_provider = id_provider

    async def __call__(self, event_id: ScheduleEventId) -> SubscriptionFull:
        subscription = await self.subscriptions_repo.get_user_subscription_by_event(
            user_id=self.id_provider.get_current_user_id(), event_id=event_id
        )
        if subscription:
            return subscription
        raise SubscriptionNotFound
