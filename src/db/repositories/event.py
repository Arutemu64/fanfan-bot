import math
from typing import List, Optional

from sqlalchemy import ColumnElement, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import Event, Nomination, Participant, Subscription, User
from .abstract import Repository


def _generate_search_terms(search_query: str) -> ColumnElement:
    return or_(
        Event.title.ilike(f"%{search_query}%"),
        Event.participant.has(
            Participant.nomination.has(Nomination.title.ilike(f"%{search_query}%"))
        ),
    )


class EventRepo(Repository[Event]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Event, session=session)

    async def new(
        self, participant: Optional[Participant] = None, title: Optional[str] = None
    ) -> Event:
        new_event = await self.session.merge(
            Event(participant=participant, title=title)
        )
        return new_event

    async def get(self, event_id: int) -> Optional[Event]:
        return await super()._get(ident=event_id)

    async def get_by_position(self, real_position: int) -> Optional[Event]:
        return await super()._get_by_where(Event.real_position == real_position)

    async def get_by_title(self, title: str) -> Optional[Event]:
        return await super()._get_by_where(Event.title == title)

    async def get_current(self) -> Optional[Event]:
        return await super()._get_by_where(Event.current.is_(True))

    async def get_next(self, event: Event) -> Optional[Event]:
        if event:
            return await super()._get_by_where(
                Event.real_position == event.real_position + 1,
            )
        else:
            return None

    async def paginate(
        self, page: int, events_per_page: int, search_query: Optional[str] = None
    ) -> Page[Event]:
        return await super()._paginate(
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
                    Event.position <= event.position,
                    _generate_search_terms(search_query),
                )
            )
        else:
            event_position = event.position
        return math.floor((event_position - 1) / events_per_page)

    async def check_user_subscribed_events(
        self, user: User, events: List[Event]
    ) -> List[Event]:
        stmt = select(Event).join(Subscription).where(Subscription.user == user)
        return (await self.session.scalars(stmt)).all()
