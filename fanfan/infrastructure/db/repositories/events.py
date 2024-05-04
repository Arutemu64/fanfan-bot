import math
from typing import Optional, Sequence

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Event, Nomination, Subscription
from fanfan.infrastructure.db.repositories.repo import Repository


def _filter_events(
    query: Select,
    search_query: str,
) -> Select:
    query = query.where(
        or_(
            Event.title.ilike(f"%{search_query}%"),
            Event.nomination.has(Nomination.title.ilike(f"%{search_query}%")),
        ),
    )
    return query


class EventsRepository(Repository[Event]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Event, session=session)

    async def get_event(self, event_id: int) -> Optional[Event]:
        return await self.session.get(Event, event_id)

    async def get_event_by_position(self, position: int) -> Optional[Event]:
        query = select(Event).where(Event.position == position).limit(1)
        return await self.session.scalar(query)

    async def get_current_event(self) -> Optional[Event]:
        query = select(Event).where(Event.current.is_(True)).limit(1)
        return await self.session.scalar(query)

    async def get_next_by_order(self, event_id: int) -> Optional[Event]:
        selected_event_order = (
            select(Event.order).where(Event.id == event_id).limit(1).scalar_subquery()
        )
        query = (
            select(Event)
            .order_by(Event.order)
            .where(Event.order > selected_event_order)
            .limit(1)
        )
        return await self.session.scalar(query)

    async def get_next_active_event(self) -> Optional[Event]:
        current_event_position = (
            select(Event.position)
            .where(Event.current.is_(True))
            .limit(1)
            .scalar_subquery()
        )
        query = (
            select(Event).where(Event.position == current_event_position + 1).limit(1)
        )
        return await self.session.scalar(query)

    async def get_all_events(self) -> Sequence[Event]:
        return (await self.session.scalars(select(Event))).all()

    async def paginate_events(
        self,
        page_number: int,
        events_per_page: int,
        search_query: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Page[Event]:
        query = (
            select(Event).order_by(Event.order).options(joinedload(Event.nomination))
        )
        if search_query:
            query = _filter_events(query, search_query)
        if user_id:
            query = query.options(contains_eager(Event.user_subscription)).outerjoin(
                Subscription,
                and_(
                    Subscription.event_id == Event.id,
                    Subscription.user_id == user_id,
                ),
            )
        return await super()._paginate(query, page_number, events_per_page)

    async def get_page_number_by_event(
        self,
        event_id: int,
        events_per_page: int,
        search_query: Optional[str] = None,
    ) -> int:
        query = select(Event.order).where(Event.id == event_id).limit(1)
        if search_query:
            query = _filter_events(
                select(func.count(Event.id)).where(Event.order <= query),
                search_query,
            )
        event_order = await self.session.scalar(query)
        page = math.ceil(math.floor(event_order) / events_per_page)
        return page - 1
