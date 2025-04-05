from sqlalchemy import Select, and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import EventORM, SubscriptionORM
from fanfan.core.dto.page import Pagination
from fanfan.core.models.event import EventId
from fanfan.core.models.subscription import (
    Subscription,
    SubscriptionFull,
    SubscriptionId,
)
from fanfan.core.models.user import UserId


class SubscriptionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(query: Select) -> Select:
        return query.options(
            joinedload(SubscriptionORM.event).options(
                undefer(EventORM.queue),
                joinedload(EventORM.nomination),
                joinedload(EventORM.block),
            ),
        )

    async def add_subscription(self, model: Subscription) -> Subscription:
        subscription = SubscriptionORM.from_model(model)
        self.session.add(subscription)
        await self.session.flush([subscription])
        return subscription.to_model()

    async def get_subscription_by_id(
        self, subscription_id: SubscriptionId
    ) -> SubscriptionFull | None:
        query = select(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
        query = self._load_full(query)
        subscription = await self.session.scalar(query)
        return subscription.to_full_model() if subscription else None

    async def get_user_subscription_by_event(
        self, user_id: UserId, event_id: EventId
    ) -> SubscriptionFull | None:
        query = select(SubscriptionORM).where(
            and_(
                SubscriptionORM.user_id == user_id,
                SubscriptionORM.event_id == event_id,
            )
        )
        query = self._load_full(query)
        subscription = await self.session.scalar(query)
        return subscription.to_full_model() if subscription else None

    async def list_subscriptions(
        self, user_id: UserId, pagination: Pagination | None = None
    ) -> list[SubscriptionFull]:
        query = (
            select(SubscriptionORM)
            .where(SubscriptionORM.user_id == user_id)
            .order_by(SubscriptionORM.event_id)
        )
        query = self._load_full(query)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        subscriptions = (await self.session.scalars(query)).all()
        return [s.to_full_model() for s in subscriptions]

    async def count_subscriptions(self, user_id: UserId) -> int:
        return await self.session.scalar(
            select(func.count(SubscriptionORM.id)).where(
                SubscriptionORM.user_id == user_id
            )
        )

    async def get_upcoming_subscriptions(self, queue: int) -> list[SubscriptionFull]:
        query = select(SubscriptionORM).where(
            SubscriptionORM.event.has(
                and_(
                    EventORM.is_skipped.isnot(True),
                    SubscriptionORM.counter >= (EventORM.queue - queue),
                    (EventORM.queue - queue) >= 0,
                ),
            ),
        )
        query = self._load_full(query)

        subscriptions = await self.session.scalars(query)
        return [s.to_full_model() for s in subscriptions]

    async def delete_subscription(self, subscription_id: SubscriptionId) -> None:
        await self.session.execute(
            delete(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
        )
