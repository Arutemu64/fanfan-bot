from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.event import UserFullEventDTO
from fanfan.core.models.page import Page, Pagination
from fanfan.infrastructure.db.models import Event, Subscription
from fanfan.infrastructure.db.queries.events import filter_events


class GetSchedulePage:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
        search_query: str | None = None,
    ) -> Page[UserFullEventDTO]:
        query = (
            select(Event)
            .order_by(Event.order)
            .options(joinedload(Event.nomination), joinedload(Event.block))
        )
        total_query = select(func.count(Event.id))

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        if search_query:
            query = filter_events(query, search_query)
            total_query = filter_events(total_query, search_query)

        if user_id := self.id_provider.get_current_user_id():
            query = query.options(contains_eager(Event.user_subscription)).outerjoin(
                Subscription,
                and_(
                    Subscription.event_id == Event.id,
                    Subscription.user_id == user_id,
                ),
            )

        events = await self.session.scalars(query)
        total = await self.session.scalar(total_query)

        return Page(
            items=[e.to_user_full_dto() for e in events],
            total=total,
        )
