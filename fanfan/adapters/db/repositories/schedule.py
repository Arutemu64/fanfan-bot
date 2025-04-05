import math

from sqlalchemy import Select, and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.adapters.db.models import (
    EventORM,
    NominationORM,
    ScheduleChangeORM,
    SubscriptionORM,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.models.event import Event, EventFull, EventId
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeFull,
    ScheduleChangeId,
)
from fanfan.core.models.user import UserId

EVENT_FULL_OPTIONS = (
    undefer(EventORM.queue),
    joinedload(EventORM.nomination),
    joinedload(EventORM.block),
)


class ScheduleRepository:
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
                    EventORM.id == int(search_query)
                    if search_query.isnumeric()
                    else False,
                    EventORM.title.ilike(f"%{search_query}%"),
                    EventORM.nomination.has(
                        NominationORM.title.ilike(f"%{search_query}%")
                    ),
                ),
            )
        return query

    @staticmethod
    def _load_full(query: Select, user_id: UserId | None = None) -> Select:
        query = query.options(*EVENT_FULL_OPTIONS)
        if user_id:
            query = query.options(contains_eager(EventORM.user_subscription)).outerjoin(
                SubscriptionORM,
                and_(
                    SubscriptionORM.event_id == EventORM.id,
                    SubscriptionORM.user_id == user_id,
                ),
            )
        return query

    async def add_schedule_change(self, model: ScheduleChange) -> ScheduleChange:
        schedule_change = ScheduleChangeORM.from_model(model)
        self.session.add(schedule_change)
        await self.session.flush([schedule_change])
        return schedule_change.to_model()

    async def save_schedule_change(self, model: ScheduleChange) -> ScheduleChange:
        schedule_change = ScheduleChangeORM.from_model(model)
        await self.session.merge(schedule_change)
        await self.session.flush([schedule_change])
        return schedule_change.to_model()

    async def get_schedule_change(
        self, schedule_change_id: ScheduleChangeId
    ) -> ScheduleChangeFull | None:
        query = (
            select(ScheduleChangeORM)
            .where(ScheduleChangeORM.id == schedule_change_id)
            .options(
                joinedload(ScheduleChangeORM.user),
                joinedload(ScheduleChangeORM.changed_event).options(
                    *EVENT_FULL_OPTIONS
                ),
                joinedload(ScheduleChangeORM.argument_event).options(
                    *EVENT_FULL_OPTIONS
                ),
            )
        )
        schedule_change = await self.session.scalar(query)
        return schedule_change.to_full_model() if schedule_change else None

    async def delete_schedule_change(
        self, schedule_change_id: ScheduleChangeId
    ) -> None:
        await self.session.execute(
            delete(ScheduleChangeORM).where(ScheduleChangeORM.id == schedule_change_id)
        )

    async def get_event_by_id(
        self, event_id: EventId, user_id: UserId | None = None
    ) -> EventFull | None:
        query = select(EventORM).where(EventORM.id == event_id)
        query = self._load_full(query, user_id)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_event_by_queue(self, queue: int) -> Event | None:
        query = select(EventORM).where(EventORM.queue == queue).limit(1)
        event = await self.session.scalar(query)
        return event.to_model() if event else None

    async def get_current_event(self) -> EventFull | None:
        query = select(EventORM).where(EventORM.is_current.is_(True))
        query = self._load_full(query)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_next_event(self) -> EventFull | None:
        current_event_order = (
            select(EventORM.order)
            .where(EventORM.is_current.is_(True))
            .scalar_subquery()
        )
        query = (
            select(EventORM)
            .order_by(EventORM.order)
            .where(
                and_(
                    EventORM.order > current_event_order,
                    EventORM.is_skipped.is_not(True),
                )
            )
            .limit(1)
        )
        query = self._load_full(query)
        event = await self.session.scalar(query)
        return event.to_full_model() if event else None

    async def get_next_by_order(self, order: float) -> Event | None:
        query = (
            select(EventORM)
            .order_by(EventORM.order)
            .where(EventORM.order > order)
            .limit(1)
        )
        event = await self.session.scalar(query)
        return event.to_model() if event else None

    async def get_previous_by_order(self, order: float) -> Event | None:
        query = (
            select(EventORM)
            .order_by(EventORM.order)
            .where(EventORM.order < order)
            .limit(1)
        )
        event = await self.session.scalar(query)
        return event.to_model() if event else None

    async def get_page_number_by_event(
        self, event_id: EventId, events_per_page: int
    ) -> int | None:
        order_query = (
            select(EventORM.order).where(EventORM.id == event_id).scalar_subquery()
        )
        position_query = select(func.count(EventORM.id)).where(
            EventORM.order <= order_query
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
    ) -> list[EventFull]:
        query = select(EventORM).order_by(EventORM.order)
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
        query = select(func.count(EventORM.id))
        if search_query:
            query = self._filter_events(query, search_query)
        return await self.session.scalar(query)

    async def save_event(self, model: Event) -> Event:
        event = await self.session.merge(EventORM.from_model(model))
        await self.session.flush([event])
        return event.to_model()
