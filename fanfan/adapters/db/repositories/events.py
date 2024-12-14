import math

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.adapters.db.models import DBEvent, DBNomination, DBSubscription
from fanfan.core.dto.page import Pagination
from fanfan.core.models.event import Event, EventId, FullEvent
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
                    DBEvent.id == int(search_query)
                    if search_query.isnumeric()
                    else False,
                    DBEvent.title.ilike(f"%{search_query}%"),
                    DBEvent.nomination.has(
                        DBNomination.title.ilike(f"%{search_query}%")
                    ),
                ),
            )
        return query

    @staticmethod
    def _load_full(query: Select, user_id: UserId | None = None) -> Select:
        query = query.options(
            undefer(DBEvent.queue),
            joinedload(DBEvent.nomination),
            joinedload(DBEvent.block),
        )
        if user_id:
            query = query.options(contains_eager(DBEvent.user_subscription)).outerjoin(
                DBSubscription,
                and_(
                    DBSubscription.event_id == DBEvent.id,
                    DBSubscription.user_id == user_id,
                ),
            )
        return query

    async def get_event_by_id(
        self, event_id: EventId, user_id: UserId | None = None
    ) -> FullEvent | None:
        query = select(DBEvent).where(DBEvent.id == event_id)
        query = self._load_full(query, user_id)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_event_by_queue(self, queue: int) -> Event | None:
        query = select(DBEvent).where(DBEvent.queue == queue).limit(1)
        event = await self.session.scalar(query)
        return event.to_model() if event else None

    async def get_current_event(self) -> FullEvent | None:
        query = select(DBEvent).where(DBEvent.is_current.is_(True))
        query = self._load_full(query)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_next_event(self) -> FullEvent | None:
        current_event_order = (
            select(DBEvent.order).where(DBEvent.is_current.is_(True)).scalar_subquery()
        )
        query = (
            select(DBEvent)
            .order_by(DBEvent.order)
            .where(
                and_(
                    DBEvent.order > current_event_order, DBEvent.is_skipped.is_not(True)
                )
            )
            .limit(1)
        )
        query = self._load_full(query)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_next_by_order(self, order: float) -> Event | None:
        query = (
            select(DBEvent)
            .order_by(DBEvent.order)
            .where(DBEvent.order > order)
            .limit(1)
        )
        event = await self.session.scalar(query)
        return event.to_model() if event else None

    async def get_page_number_by_event(
        self, event_id: EventId, events_per_page: int
    ) -> int | None:
        order_query = (
            select(DBEvent.order).where(DBEvent.id == event_id).scalar_subquery()
        )
        position_query = select(func.count(DBEvent.id)).where(
            DBEvent.order <= order_query
        )
        event_position = await self.session.scalar(position_query)
        if event_position > 0:
            return math.floor((event_position - 1) / events_per_page)
        return None

    async def list_events(
        self,
        search_query: str | None = None,
        pagination: Pagination | None = None,
        user_id: UserId | None = None,
    ) -> list[FullEvent]:
        query = select(DBEvent).order_by(DBEvent.order)
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
        query = select(func.count(DBEvent.id))
        if search_query:
            query = self._filter_events(query, search_query)
        return await self.session.scalar(query)

    async def save_event(self, model: Event) -> Event:
        event = await self.session.merge(DBEvent.from_model(model))
        await self.session.flush([event])
        return event.to_model()
