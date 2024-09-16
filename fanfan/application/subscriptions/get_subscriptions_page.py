from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.page import Page, Pagination
from fanfan.core.models.subscription import FullSubscriptionDTO
from fanfan.infrastructure.db.models import Event, Subscription


class GetSubscriptionsPage:
    def __init__(
        self,
        session: AsyncSession,
        id_provider: IdProvider,
    ) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[FullSubscriptionDTO]:
        query = (
            select(Subscription)
            .where(Subscription.user_id == self.id_provider.get_current_user_id())
            .order_by(Subscription.event_id)
            .options(joinedload(Subscription.event).undefer(Event.queue))
        )

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        subscriptions = await self.session.scalars(query)
        total = await self.session.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.user_id == self.id_provider.get_current_user_id()
            )
        )

        return Page(
            items=[s.to_full_dto() for s in subscriptions],
            total=total,
        )
