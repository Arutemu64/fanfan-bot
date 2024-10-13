from fanfan.application.schedule_mgmt.set_current_event import (
    SetCurrentEvent,
    SetCurrentEventResult,
)
from fanfan.core.exceptions.events import NoNextEvent
from fanfan.infrastructure.db.repositories.events import EventsRepository


class SetNextEvent:
    def __init__(
        self,
        events_repo: EventsRepository,
        set_current_event: SetCurrentEvent,
    ):
        self.events_repo = events_repo
        self.set_current_event = set_current_event

    async def __call__(self) -> SetCurrentEventResult:
        next_event = await self.events_repo.get_next_event()
        if next_event is None:
            next_event = await self.events_repo.get_event_by_queue(1)
            if next_event is None:
                raise NoNextEvent
        return await self.set_current_event(next_event.id)
