from typing import List, Optional

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.application.dto.common import Page
from fanfan.application.dto.subscription import (
    CreateSubscriptionDTO,
    FullSubscriptionDTO,
    SubscriptionDTO,
)
from fanfan.infrastructure.db.models import Event, Subscription
from fanfan.infrastructure.db.repositories.repo import Repository


class SubscriptionsRepository(Repository[Subscription]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Subscription, session=session)

    async def add_subscription(self, dto: CreateSubscriptionDTO) -> SubscriptionDTO:
        subscription = Subscription(**dto.model_dump(exclude_unset=True))
        self.session.add(subscription)
        await self.session.flush([subscription])
        return subscription.to_dto()

    async def get_subscription(
        self, subscription_id: int
    ) -> Optional[FullSubscriptionDTO]:
        subscription = await self.session.get(
            Subscription,
            subscription_id,
            options=[joinedload(Subscription.event).undefer(Event.position)],
        )
        return subscription.to_full_dto() if subscription else None

    async def get_subscription_by_event(
        self,
        user_id: int,
        event_id: int,
    ) -> Optional[FullSubscriptionDTO]:
        query = (
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user_id, Subscription.event_id == event_id
                ),
            )
            .limit(1)
            .options(joinedload(Subscription.event).undefer(Event.position))
        )
        subscription = await self.session.scalar(query)
        return subscription.to_full_dto() if subscription else None

    async def paginate_subscriptions(
        self,
        page_number: int,
        subscriptions_per_page: int,
        user_id: int,
    ) -> Page[FullSubscriptionDTO]:
        query = (
            select(Subscription)
            .where(
                and_(Subscription.user_id == user_id),
            )
            .order_by(Subscription.event_id)
            .options(joinedload(Subscription.event).undefer(Event.position))
        )
        page = await super()._paginate(query, page_number, subscriptions_per_page)
        return Page(
            items=[s.to_full_dto() for s in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )

    async def get_upcoming_subscriptions(self) -> List[FullSubscriptionDTO]:
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
            .options(joinedload(Subscription.event).undefer(Event.position))
        )
        return [s.to_full_dto() for s in (await self.session.scalars(query)).all()]

    async def delete_subscription(self, subscription_id: int) -> None:
        await self.session.execute(
            delete(Subscription).where(Subscription.id == subscription_id)
        )

    async def bulk_delete_subscriptions(self, event_id: int) -> None:
        await self.session.execute(
            delete(Subscription).where(Subscription.event_id == event_id)
        )
