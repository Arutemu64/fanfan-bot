import math
from typing import Optional, Sequence

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from fanfan.infrastructure.db.models import Event, Nomination, Subscription
from fanfan.infrastructure.db.repositories.repo import Repository


def _build_events_query(
    query: Select, search_query: Optional[str] = None, user_id: Optional[int] = None
) -> Select:
    if search_query:
        query = query.where(
            or_(
                Event.title.ilike(f"%{search_query}%"),
                Event.nomination.has(Nomination.title.ilike(f"%{search_query}%")),
            )
        )
    if user_id:
        query = query.options(contains_eager(Event.user_subscription)).outerjoin(
            Subscription,
            and_(
                Subscription.event_id == Event.id,
                Subscription.user_id == user_id,
            ),
        )
    return query


class EventsRepository(Repository[Event]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Event, session=session)

    async def get_event(self, event_id: int) -> Optional[Event]:
        return await self.session.get(Event, event_id)

    async def get_event_by_real_position(self, real_position: int) -> Optional[Event]:
        query = select(Event).where(Event.real_position == real_position).limit(1)
        return await self.session.scalar(query)

    async def get_current_event(self) -> Optional[Event]:
        query = select(Event).where(Event.current.is_(True)).limit(1)
        return await self.session.scalar(query)

    async def get_next_event(self, event_id: int) -> Optional[Event]:
        event_position = (
            select(Event.position)
            .where(Event.id == event_id)
            .limit(1)
            .scalar_subquery()
        )
        query = (
            select(Event)
            .order_by(Event.position)
            .where(and_(Event.position > event_position, Event.skip.isnot(True)))
            .limit(1)
        )
        return await self.session.scalar(query)

    async def paginate_events(
        self,
        page: int,
        events_per_page: int,
        search_query: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Sequence[Event]:
        query = _build_events_query(
            select(Event), search_query=search_query, user_id=user_id
        )
        query = (
            query.order_by(Event.position)
            .slice(
                start=(page * events_per_page),
                stop=(page * events_per_page) + events_per_page,
            )
            .options(joinedload(Event.nomination))
        )
        return (await self.session.scalars(query)).all()

    async def count_events(self, search_query: Optional[str] = None) -> int:
        query = _build_events_query(
            select(func.count(Event.id)), search_query=search_query
        )
        return await self.session.scalar(query)

    async def get_page_number_by_event(
        self, event_id: int, events_per_page: int, search_query: Optional[str] = None
    ) -> int:
        query = select(Event.position).where(Event.id == event_id).limit(1)
        if search_query:
            subquery = query.scalar_subquery()
            query = _build_events_query(query, search_query=search_query).where(
                Event.position <= subquery
            )
        event_position = await self.session.scalar(query)
        return math.floor((event_position - 1) / events_per_page)
