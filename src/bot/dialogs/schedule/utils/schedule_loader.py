import math
from typing import List

from sqlalchemy import ColumnElement, and_, func, or_, select, true

from src.db import Database
from src.db.models import Event, Nomination, Participant


class ScheduleLoader:
    def __init__(
        self,
        db: Database,
        events_per_page: int,
        include_hidden: bool,
        search_query: str = None,
    ):
        self.db = db
        self.events_per_page = events_per_page
        self.include_hidden = include_hidden
        self.search_query = search_query

    def _get_query(self) -> ColumnElement:
        query = [true()]
        if self.search_query:
            if self.search_query.isnumeric():
                query.append(Event.id == int(self.search_query))
            else:
                query.append(
                    or_(
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
                )
        if not self.include_hidden:
            query.append(Event.hidden.isnot(True))
        return and_(*query)

    async def get_pages_count(self) -> int:
        if self.search_query:
            events_count = await self.db.event.get_count(query=self._get_query())
        else:
            if self.include_hidden:
                events_count = (
                    await self.db.session.execute(select(func.max(Event.position)))
                ).scalar()
            else:
                events_count = (
                    await self.db.session.execute(
                        select(func.max(Event.real_position)).select_from(Event)
                    )
                ).scalar()
        return math.ceil(events_count / self.events_per_page)

    async def get_page_number(self, event: Event) -> int:
        if self.search_query:
            event_position = await self.db.event.get_count(
                and_(Event.position < event.position, self._get_query())
            )
        else:
            if self.include_hidden:
                event_position = event.position
            else:
                event_position = event.real_position
        return math.floor((event_position - 1) / self.events_per_page)

    async def get_page_events(self, page: int) -> List[Event]:
        events = await self.db.event.get_range(
            start=(page * self.events_per_page),
            end=(page * self.events_per_page) + self.events_per_page,
            query=self._get_query(),
            order_by=Event.position,
        )
        return events
