from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.events import EventNotFound, NoNextEvent
from fanfan.infrastructure.db.models import Event
from fanfan.infrastructure.db.queries.events import next_event_query

from .set_current_event import SetCurrentEvent, SetCurrentEventResult


class SetNextEvent:
    def __init__(self, session: AsyncSession, set_current_event: SetCurrentEvent):
        self.session = session
        self.set_current_event = set_current_event

    async def __call__(self) -> SetCurrentEventResult:
        next_event = await self.session.scalar(next_event_query())
        if next_event is None:
            current_event = await self.session.scalar(
                select(Event).where(Event.current.is_(True))
            )
            if current_event:
                raise NoNextEvent
            next_event = await self.session.scalar(
                select(Event).where(Event.queue == 1)
            )
            if next_event is None:
                raise EventNotFound
        return await self.set_current_event(next_event.id)
