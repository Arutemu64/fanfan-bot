from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import Event, Subscription
from .abstract import Repository


class SubscriptionRepo(Repository[Subscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Subscription, session=session)

    async def new(
        self,
        event_id: int,
        user_id: int,
        counter: Optional[int] = None,
    ) -> Subscription:
        new_subscription = await self.session.merge(
            Subscription(
                event_id=event_id,
                user_id=user_id,
                counter=counter,
            )
        )
        return new_subscription

    async def paginate(
        self, page: int, subscriptions_per_page: int, user_id: int
    ) -> Page[Subscription]:
        return await super()._paginate(
            page=page,
            items_per_page=subscriptions_per_page,
            query=Subscription.user_id == user_id,
            order_by=Subscription.event_id,
        )

    async def get_subscription_for_user(
        self, event_id: int, user_id: int
    ) -> Optional[Subscription]:
        query = and_(
            Subscription.event_id == event_id,
            Subscription.user_id == user_id,
        )
        return await super()._get_by_where(
            query=query,
        )

    async def check_user_subscribed_event_ids(
        self, user_id: int, event_ids: List[int]
    ) -> List[Event.id]:
        stmt = (
            select(Event.id).join(
                Subscription,
                and_(
                    Subscription.event_id == Event.id, Subscription.user_id == user_id
                ),
            )
        ).where(Event.id.in_(event_ids))
        return [r[0] for r in (await self.session.execute(stmt)).all()]

    async def get_all_upcoming(self, event: Event) -> List[Subscription]:
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

    async def delete(self, subscription_id: int):
        await super()._delete(Subscription.id == subscription_id)

    async def batch_delete(self, subscription_ids: List[int]):
        await super()._delete(Subscription.id.in_(subscription_ids))
