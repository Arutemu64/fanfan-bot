from typing import Optional, Sequence

from sqlalchemy import Select, and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.infrastructure.db.models import Event, Subscription
from fanfan.infrastructure.db.repositories.repo import Repository


def _build_subscriptions_query(query: Select, user_id: Optional[int] = None) -> Select:
    if user_id:
        query = query.where(Subscription.user_id == user_id)
    return query


class SubscriptionsRepository(Repository[Subscription]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Subscription, session=session)

    async def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        return await self.session.get(
            Subscription, subscription_id, options=[joinedload(Subscription.event)]
        )

    async def get_subscription_by_event(
        self, user_id: int, event_id: int
    ) -> Optional[Subscription]:
        query = (
            select(Subscription)
            .where(
                and_(Subscription.user_id == user_id, Subscription.event_id == event_id)
            )
            .limit(1)
            .options(joinedload(Subscription.event))
        )
        return await self.session.scalar(query)

    async def paginate_subscriptions(
        self, page: int, subscriptions_per_page: int, user_id: int
    ) -> Sequence[Subscription]:
        query = _build_subscriptions_query(select(Subscription), user_id=user_id)
        query = (
            query.order_by(Subscription.event_id)
            .slice(
                start=(page * subscriptions_per_page),
                stop=(page * subscriptions_per_page) + subscriptions_per_page,
            )
            .options(joinedload(Subscription.event))
        )
        return (await self.session.scalars(query)).all()

    async def count_subscriptions(self, user_id: int) -> int:
        query = _build_subscriptions_query(
            select(func.count(Subscription.id)), user_id=user_id
        )
        return await self.session.scalar(query)

    async def get_upcoming_subscriptions(self) -> Sequence[Subscription]:
        event_real_position = (
            select(Event.real_position)
            .where(Event.current.is_(True))
            .limit(1)
            .scalar_subquery()
        )
        query = (
            select(Subscription)
            .where(
                Subscription.event.has(
                    and_(
                        Event.skip.isnot(True),
                        Subscription.counter
                        >= (Event.real_position - event_real_position),
                        (Event.real_position - event_real_position) >= 0,
                    ),
                )
            )
            .options(joinedload(Subscription.event))
        )
        return (await self.session.scalars(query)).all()

    async def bulk_delete_subscriptions_by_event(self, event_id: int) -> None:
        query = delete(Subscription).where(Subscription.event_id == event_id)
        await self.session.execute(query)
