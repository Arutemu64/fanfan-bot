import math
from typing import List

from sqlalchemy import ColumnElement, and_, func, or_, select

from src.db import Database
from src.db.models import Event, Nomination, Participant, Subscription


class ScheduleLoader:
    def __init__(
        self,
        db: Database,
        events_per_page: int,
        search_query: str = None,
    ):
        self.db = db
        self.events_per_page = events_per_page
        self.search_query = search_query

    def _get_search_query(self) -> ColumnElement:
        if self.search_query.isnumeric():
            query = Event.id == int(self.search_query)
        else:
            query = or_(
                Event.title.ilike(f"%{self.search_query}%"),
                Event.participant.has(
                    Participant.title.ilike(f"%{self.search_query}%")
                ),
                Event.participant.has(
                    Participant.nomination.has(
                        Nomination.title.ilike(f"%{self.search_query}%")
                    )
                ),
            )
        return query

    async def get_pages_count(self) -> int:
        if self.search_query:
            events_count = await self.db.event.get_count(query=self._get_search_query())
        else:
            events_count = (
                await self.db.session.execute(select(func.max(Event.position)))
            ).scalar()
        return math.ceil(events_count / self.events_per_page)

    async def get_page_number(self, event: Event) -> int:
        if self.search_query:
            event_position = await self.db.event.get_count(
                and_(Event.position < event.position, self._get_search_query())
            )
        else:
            event_position = event.position
        return math.floor((event_position - 1) / self.events_per_page)

    async def get_page_events(self, page: int, user_id: int = None) -> List[Event]:
        stmt = (
            select(Event, Subscription.event_id)
            .order_by(Event.position)
            .slice(
                start=(page * self.events_per_page),
                stop=(page * self.events_per_page) + self.events_per_page,
            )
        )
        if self.search_query:
            stmt = stmt.where(self._get_search_query())
        if user_id:
            stmt = stmt.outerjoin(
                Subscription,
                and_(
                    Subscription.event_id == Event.id, Subscription.user_id == user_id
                ),
            )
        return (await self.db.session.execute(stmt)).all()
