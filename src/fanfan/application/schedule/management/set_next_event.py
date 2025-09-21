from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.application.schedule.management.set_current_event import (
    SetCurrentScheduleEvent,
    SetCurrentScheduleEventDTO,
    SetCurrentScheduleEventResult,
)
from fanfan.core.exceptions.schedule import NoNextEvent


class SetNextScheduleEvent:
    def __init__(
        self,
        schedule_repo: ScheduleEventsRepository,
        set_current_event: SetCurrentScheduleEvent,
    ):
        self.schedule_repo = schedule_repo
        self.set_current_event = set_current_event

    async def __call__(self) -> SetCurrentScheduleEventResult:
        current_event = await self.schedule_repo.get_current_event()
        if current_event:
            next_event = await self.schedule_repo.read_next_event()
            if next_event is None:
                raise NoNextEvent
        else:
            next_event = await self.schedule_repo.read_event_by_queue(1)
            if next_event is None:
                raise NoNextEvent
        return await self.set_current_event(
            SetCurrentScheduleEventDTO(event_id=next_event.id)
        )
