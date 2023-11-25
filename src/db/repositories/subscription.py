from typing import Optional, Sequence

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import Event, Subscription, User
from .abstract import Repository


class SubscriptionRepo(Repository[Subscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Subscription, session=session)

    async def new(
        self,
        user: User,
        event: Event,
        counter: Optional[int] = None,
    ) -> Subscription:
        new_subscription = await self.session.merge(
            Subscription(
                event=event,
                user=user,
                counter=counter,
            )
        )
        return new_subscription

    async def paginate(
        self, page: int, user: User, subscriptions_per_page: int
    ) -> Page[Subscription]:
        return await super()._paginate(
            page=page,
            items_per_page=subscriptions_per_page,
            query=Subscription.user == user,
            order_by=Subscription.event_id,
        )

    async def get_subscription_for_user(
        self,
        user: User,
        event: Event,
    ) -> Optional[Subscription]:
        query = and_(
            Subscription.user == user,
            Subscription.event == event,
        )
        return await super()._get_by_where(query=query)

    async def get_all_upcoming(self, event: Event) -> Sequence[Subscription]:
        query = Subscription.event.has(
            and_(
                Event.skip.isnot(True),
                Subscription.counter >= (Event.real_position - event.real_position),
                (Event.real_position - event.real_position) >= 0,
            ),
        )
        return await super()._get_many(
            query=query,
            order_by=Subscription.event_id,
        )
