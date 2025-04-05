from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.application.schedule_mgmt.set_current_event import (
    SetCurrentEvent,
    SetCurrentEventResult,
)
from fanfan.core.exceptions.schedule import NoNextEvent


class SetNextEvent:
    def __init__(
        self,
        events_repo: ScheduleRepository,
        set_current_event: SetCurrentEvent,
    ):
        self.events_repo = events_repo
        self.set_current_event = set_current_event

    async def __call__(self) -> SetCurrentEventResult:
        next_event = await self.events_repo.get_next_event()
        if next_event is None:
            next_event = await self.events_repo.get_event_by_queue(1)
            if (next_event is None) or next_event.is_current:
                raise NoNextEvent
        return await self.set_current_event(next_event.id)
