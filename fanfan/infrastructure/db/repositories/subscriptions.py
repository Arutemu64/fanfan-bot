from typing import Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Event, Subscription
from fanfan.infrastructure.db.repositories.repo import Repository


class SubscriptionsRepository(Repository[Subscription]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Subscription, session=session)

    async def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        return await self.session.get(
            Subscription,
            subscription_id,
            options=[joinedload(Subscription.event)],
        )

    async def get_subscription_by_event(
        self,
        user_id: int,
        event_id: int,
    ) -> Optional[Subscription]:
        query = (
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user_id, Subscription.event_id == event_id
                ),
            )
            .limit(1)
            .options(joinedload(Subscription.event))
        )
        return await self.session.scalar(query)

    async def paginate_subscriptions(
        self,
        page_number: int,
        subscriptions_per_page: int,
        user_id: int,
    ) -> Page[Subscription]:
        query = (
            select(Subscription)
            .where(
                and_(Subscription.user_id == user_id),
            )
            .order_by(Subscription.event_id)
            .options(joinedload(Subscription.event))
        )
        return await super()._paginate(query, page_number, subscriptions_per_page)

    async def get_upcoming_subscriptions(self) -> Sequence[Subscription]:
        event_position = (
            select(Event.position)
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
                        Subscription.counter >= (Event.position - event_position),
                        (Event.position - event_position) >= 0,
                    ),
                ),
            )
            .options(joinedload(Subscription.event))
        )
        return (await self.session.scalars(query)).all()
