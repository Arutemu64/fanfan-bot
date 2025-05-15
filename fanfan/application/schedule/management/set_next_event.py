from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.application.schedule.management.set_current_event import (
    SetCurrentEvent,
    SetCurrentEventResult,
)
from fanfan.core.exceptions.schedule import NoNextEvent


class SetNextEvent:
    def __init__(
        self,
        schedule_repo: ScheduleEventsRepository,
        set_current_event: SetCurrentEvent,
    ):
        self.schedule_repo = schedule_repo
        self.set_current_event = set_current_event

    async def __call__(self) -> SetCurrentEventResult:
        next_event = await self.schedule_repo.read_next_event()
        if next_event is None:
            next_event = await self.schedule_repo.read_event_by_queue(1)
            if (next_event is None) or next_event.is_current:
                raise NoNextEvent
        return await self.set_current_event(next_event.id)
