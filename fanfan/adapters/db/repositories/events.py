import math

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.adapters.db.models import Event, Nomination, Subscription
from fanfan.core.dto.page import Pagination
from fanfan.core.models.event import EventId, EventModel, FullEventModel
from fanfan.core.models.user import UserId


class EventsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _filter_events(
        query: Select,
        search_query: str | None,
    ) -> Select:
        if search_query:
            query = query.where(
                or_(
                    Event.id == int(search_query)
                    if search_query.isnumeric()
                    else False,
                    Event.title.ilike(f"%{search_query}%"),
                    Event.nomination.has(Nomination.title.ilike(f"%{search_query}%")),
                ),
            )
        return query

    @staticmethod
    def _load_full(query: Select, user_id: UserId | None = None) -> Select:
        query = query.options(
            undefer(Event.queue), joinedload(Event.nomination), joinedload(Event.block)
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

    async def get_event_by_id(
        self, event_id: EventId, user_id: UserId | None = None
    ) -> FullEventModel | None:
        query = select(Event).where(Event.id == event_id)
        query = self._load_full(query, user_id)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_event_by_queue(self, queue: int) -> EventModel | None:
        query = select(Event).where(Event.queue == queue).limit(1)
        event = await self.session.scalar(query)
        return event.to_model() if event else None

    async def get_current_event(self) -> FullEventModel | None:
        query = select(Event).where(Event.current.is_(True))
        query = self._load_full(query)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_next_event(self) -> FullEventModel | None:
        current_event_order = (
            select(Event.order).where(Event.current.is_(True)).scalar_subquery()
        )
        query = (
            select(Event)
            .order_by(Event.order)
            .where(and_(Event.order > current_event_order, Event.skip.is_not(True)))
            .limit(1)
        )
        query = self._load_full(query)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_next_by_order(self, order: float) -> EventModel | None:
        query = select(Event).order_by(Event.order).where(Event.order > order).limit(1)
        event = await self.session.scalar(query)
        return event.to_model() if event else None

    async def get_page_number_by_event(
        self, event_id: EventId, events_per_page: int
    ) -> int | None:
        order_query = select(Event.order).where(Event.id == event_id).scalar_subquery()
        position_query = select(func.count(Event.id)).where(Event.order <= order_query)
        event_position = await self.session.scalar(position_query)
        if event_position > 0:
            return math.floor((event_position - 1) / events_per_page)
        return None

    async def list_events(
        self,
        search_query: str | None = None,
        pagination: Pagination | None = None,
        user_id: UserId | None = None,
    ) -> list[FullEventModel]:
        query = select(Event).order_by(Event.order)
        query = self._load_full(query, user_id)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)
        if search_query:
            query = self._filter_events(query, search_query)

        events = await self.session.scalars(query)
        return [e.to_full_model() for e in events]

    async def count_events(
        self,
        search_query: str | None = None,
    ) -> int:
        query = select(func.count(Event.id))
        if search_query:
            query = self._filter_events(query, search_query)
        return await self.session.scalar(query)

    async def save_event(self, model: EventModel) -> EventModel:
        event = await self.session.merge(Event.from_model(model))
        await self.session.flush([event])
        return event.to_model()
