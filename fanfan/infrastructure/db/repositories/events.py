import math
from typing import List, Optional

from sqlalchemy import Select, and_, case, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.application.dto.common import Page
from fanfan.application.dto.event import (
    CreateEventDTO,
    EventDTO,
    FullEventDTO,
    ScheduleEventDTO,
    UpdateEventDTO,
)
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

    async def add_event(self, dto: CreateEventDTO) -> EventDTO:
        event = Event(**dto.model_dump(exclude_unset=True))
        self.session.add(event)
        await self.session.flush([event])
        return event.to_dto()

    async def get_event(
        self, event_id: int, user_id: Optional[int] = None
    ) -> Optional[FullEventDTO]:
        query = (
            select(Event)
            .where(Event.id == event_id)
            .limit(1)
            .options(joinedload(Event.nomination), undefer(Event.position))
        )
        if user_id:
            query = query.options(contains_eager(Event.user_subscription)).outerjoin(
                Subscription,
                and_(
                    Subscription.event_id == Event.id,
                    Subscription.user_id == user_id,
                ),
            )
        event = await self.session.scalar(query)
        return event.to_full_dto() if event else None

    async def get_current_event(self) -> Optional[FullEventDTO]:
        query = select(Event).where(Event.current.is_(True)).limit(1)
        query = query.options(joinedload(Event.nomination), undefer(Event.position))
        event = await self.session.scalar(query)
        return event.to_full_dto() if event else None

    async def get_next_event(self) -> Optional[FullEventDTO]:
        current_event_position = (
            select(Event.position)
            .where(Event.current.is_(True))
            .limit(1)
            .scalar_subquery()
        )
        # If current event exists, select event next to it
        # If not - pick first event
        query = (
            select(Event)
            .where(
                case(
                    (
                        current_event_position.is_not(None),
                        Event.position == current_event_position + 1,
                    ),
                    else_=Event.position == 1,
                )
            )
            .limit(1)
        )
        query = query.options(joinedload(Event.nomination), undefer(Event.position))
        event = await self.session.scalar(query)
        return event.to_dto() if event else None

    async def get_next_by_order(self, event_id: int) -> Optional[FullEventDTO]:
        selected_event_order = (
            select(Event.order).where(Event.id == event_id).limit(1).scalar_subquery()
        )
        query = (
            select(Event)
            .order_by(Event.order)
            .where(Event.order > selected_event_order)
            .limit(1)
        )
        query = query.options(joinedload(Event.nomination), undefer(Event.position))
        event = await self.session.scalar(query)
        return event.to_dto() if event else None

    async def get_all_events(self) -> List[EventDTO]:
        return [e.to_dto() for e in (await self.session.scalars(select(Event))).all()]

    async def paginate_events(
        self,
        page_number: int,
        events_per_page: int,
        search_query: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Page[ScheduleEventDTO]:
        query = select(Event).order_by(Event.order)
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
        query = query.options(joinedload(Event.nomination))
        page = await super()._paginate(query, page_number, events_per_page)
        return Page(
            items=[e.to_schedule_dto() for e in page.items],
            number=page.number,
            total_pages=page.total_pages if page.total_pages > 0 else 1,
        )

    async def get_page_number_by_event(
        self,
        event_id: int,
        events_per_page: int,
        search_query: Optional[str] = None,
    ) -> Optional[int]:
        order_query = (
            select(Event.order).where(Event.id == event_id).limit(1).scalar_subquery()
        )
        position_query = select(func.count(Event.id)).where(Event.order <= order_query)
        if search_query:
            position_query = _filter_events(
                position_query,
                search_query,
            )
        event_position = await self.session.scalar(position_query)
        if event_position > 0:
            page_number = math.floor((event_position - 1) / events_per_page)
            return page_number
        else:
            return None

    async def update_event(self, dto: UpdateEventDTO) -> None:
        await self.session.execute(
            update(Event)
            .where(Event.id == dto.id)
            .values(**dto.model_dump(exclude_unset=True))
        )

    async def delete_event(self, event_id: int) -> None:
        await self.session.execute(delete(Event).where(Event.id == event_id))
