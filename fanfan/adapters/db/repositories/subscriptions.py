from sqlalchemy import Select, and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import Event, Subscription
from fanfan.core.dto.page import Pagination
from fanfan.core.models.event import EventId
from fanfan.core.models.subscription import (
    FullSubscriptionModel,
    SubscriptionId,
    SubscriptionModel,
)
from fanfan.core.models.user import UserId


class SubscriptionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(query: Select) -> Select:
        return query.options(
            joinedload(Subscription.event).options(
                undefer(Event.queue),
                joinedload(Event.nomination),
                joinedload(Event.block),
            ),
        )

    async def add_subscription(self, model: SubscriptionModel) -> SubscriptionModel:
        subscription = Subscription.from_model(model)
        self.session.add(subscription)
        await self.session.flush([subscription])
        return subscription.to_model()

    async def get_subscription_by_id(
        self, subscription_id: SubscriptionId
    ) -> FullSubscriptionModel | None:
        query = select(Subscription).where(Subscription.id == subscription_id)
        query = self._load_full(query)
        subscription = await self.session.scalar(query)
        return subscription.to_full_model() if subscription else None

    async def get_user_subscription_by_event(
        self, user_id: UserId, event_id: EventId
    ) -> FullSubscriptionModel | None:
        query = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.event_id == event_id,
            )
        )
        query = self._load_full(query)
        subscription = await self.session.scalar(query)
        return subscription.to_full_model() if subscription else None

    async def list_subscriptions(
        self, user_id: UserId, pagination: Pagination | None = None
    ) -> list[FullSubscriptionModel]:
        query = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.event_id)
        )
        query = self._load_full(query)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        subscriptions = (await self.session.scalars(query)).all()
        return [s.to_full_model() for s in subscriptions]

    async def count_subscriptions(self, user_id: UserId) -> int:
        return await self.session.scalar(
            select(func.count(Subscription.id)).where(Subscription.user_id == user_id)
        )

    async def get_upcoming_subscriptions(self) -> list[FullSubscriptionModel]:
        event_position = (
            select(Event.queue).where(Event.is_current.is_(True)).scalar_subquery()
        )
        query = select(Subscription).where(
            Subscription.event.has(
                and_(
                    Event.is_skipped.isnot(True),
                    Subscription.counter >= (Event.queue - event_position),
                    (Event.queue - event_position) >= 0,
                ),
            ),
        )
        query = self._load_full(query)

        subscriptions = await self.session.scalars(query)
        return [s.to_full_model() for s in subscriptions]

    async def delete_subscription(self, subscription_id: SubscriptionId) -> None:
        await self.session.execute(
            delete(Subscription).where(Subscription.id == subscription_id)
        )
