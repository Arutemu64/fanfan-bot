import math
from typing import List, Optional

from sqlalchemy import ColumnElement, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Event, Nomination, Participant
from .abstract import Repository


def _generate_search_terms(search_query: str) -> ColumnElement:
    return or_(
        Event.joined_title.ilike(f"%{search_query}%"),
        Event.participant.has(
            Participant.nomination.has(Nomination.title.ilike(f"%{search_query}%"))
        ),
    )


class EventRepo(Repository[Event]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Event, session=session)

    async def new(
        self, participant_id: Optional[int] = None, title: Optional[str] = None
    ) -> Event:
        new_event = await self.session.merge(
            Event(participant_id=participant_id, title=title)
        )
        return new_event

    async def get(self, event_id: int) -> Optional[Event]:
        return await super()._get(ident=event_id)

    async def get_by_position(self, position: int) -> Optional[Event]:
        return await super()._get_by_where(Event.real_position == position)

    async def get_current(self) -> Optional[Event]:
        return await super()._get_by_where(Event.current.is_(True))

    async def get_next(self, event: Event) -> Optional[Event]:
        if event:
            return await super()._get_by_where(
                Event.real_position == event.real_position + 1,
            )
        else:
            return None

    async def get_count(
        self,
        search_query: Optional[str] = None,
        skipped: Optional[bool] = None,
    ) -> int:
        terms = []
        if search_query:
            terms.append(_generate_search_terms(search_query))
        if skipped is not None:
            terms.append(Event.skip.is_(skipped))
        return await super()._get_count(query=and_(*terms))

    async def get_pages_count(
        self, events_per_page: int, search_query: Optional[str] = None
    ) -> int:
        events_count = await super()._get_count(
            query=_generate_search_terms(search_query) if search_query else None
        )
        return math.ceil(events_count / events_per_page)

    async def get_page(
        self, page: int, events_per_page: int, search_query: Optional[str] = None
    ) -> List[Event]:
        return await super()._get_page(
            page=page,
            items_per_page=events_per_page,
            query=_generate_search_terms(search_query) if search_query else None,
            order_by=Event.position,
        )

    async def get_page_number(
        self,
        event: Event,
        events_per_page: int,
        search_query: Optional[str] = None,
    ) -> int:
        if search_query:
            event_position = await super()._get_count(
                and_(
                    Event.position < event.position,
                    Event.joined_title.ilike(f"%{search_query}%"),
                )
            )
        else:
            event_position = event.position
        return math.floor((event_position - 1) / events_per_page)
