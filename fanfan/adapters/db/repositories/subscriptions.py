from sqlalchemy import Select, and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import ScheduleEventORM, SubscriptionORM
from fanfan.core.dto.page import Pagination
from fanfan.core.models.schedule_event import ScheduleEventId
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
    def _load_full(stmt: Select) -> Select:
        return stmt.options(
            joinedload(SubscriptionORM.event).options(
                undefer(ScheduleEventORM.queue),
                joinedload(ScheduleEventORM.nomination),
                joinedload(ScheduleEventORM.block),
            ),
        )

    async def add_subscription(self, subscription: Subscription) -> Subscription:
        subscription_orm = SubscriptionORM.from_model(subscription)
        self.session.add(subscription_orm)
        await self.session.flush([subscription_orm])
        return subscription_orm.to_model()

    async def get_subscription_by_id(
        self, subscription_id: SubscriptionId
    ) -> SubscriptionFull | None:
        stmt = select(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
        stmt = self._load_full(stmt)
        subscription_orm = await self.session.scalar(stmt)
        return subscription_orm.to_full_model() if subscription_orm else None

    async def get_user_subscription_by_event(
        self, user_id: UserId, event_id: ScheduleEventId
    ) -> SubscriptionFull | None:
        stmt = select(SubscriptionORM).where(
            and_(
                SubscriptionORM.user_id == user_id,
                SubscriptionORM.event_id == event_id,
            )
        )
        stmt = self._load_full(stmt)
        subscription_orm = await self.session.scalar(stmt)
        return subscription_orm.to_full_model() if subscription_orm else None

    async def list_subscriptions(
        self, user_id: UserId, pagination: Pagination | None = None
    ) -> list[SubscriptionFull]:
        stmt = (
            select(SubscriptionORM)
            .where(SubscriptionORM.user_id == user_id)
            .order_by(SubscriptionORM.event_id)
        )
        stmt = self._load_full(stmt)

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        subscriptions_orm = (await self.session.scalars(stmt)).all()
        return [s.to_full_model() for s in subscriptions_orm]

    async def count_subscriptions(self, user_id: UserId) -> int:
        return await self.session.scalar(
            select(func.count(SubscriptionORM.id)).where(
                SubscriptionORM.user_id == user_id
            )
        )

    async def get_upcoming_subscriptions(self, queue: int) -> list[SubscriptionFull]:
        stmt = select(SubscriptionORM).where(
            SubscriptionORM.event.has(
                and_(
                    ScheduleEventORM.is_skipped.isnot(True),
                    SubscriptionORM.counter >= (ScheduleEventORM.queue - queue),
                    (ScheduleEventORM.queue - queue) >= 0,
                ),
            ),
        )
        stmt = self._load_full(stmt)

        subscriptions_orm = await self.session.scalars(stmt)
        return [s.to_full_model() for s in subscriptions_orm]

    async def delete_subscription(self, subscription: Subscription) -> None:
        await self.session.execute(
            delete(SubscriptionORM).where(SubscriptionORM.id == subscription.id)
        )
