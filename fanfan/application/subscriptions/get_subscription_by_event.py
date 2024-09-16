from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.subscriptions import SubscriptionNotFound
from fanfan.core.models.subscription import FullSubscriptionDTO
from fanfan.infrastructure.db.models import Subscription


class GetSubscriptionByEvent:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(self, event_id: int) -> FullSubscriptionDTO:
        subscription = await self.session.scalar(
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == self.id_provider.get_current_user_id(),
                    Subscription.event_id == event_id,
                ),
            )
            .limit(1)
            .options(joinedload(Subscription.event))
        )
        if subscription:
            return subscription.to_full_dto()
        raise SubscriptionNotFound
