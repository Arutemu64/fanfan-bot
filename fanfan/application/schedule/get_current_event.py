from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.core.exceptions.schedule import NoCurrentEvent
from fanfan.core.models.schedule_event import ScheduleEventFull


class GetCurrentEvent:
    def __init__(self, events_repo: ScheduleRepository) -> None:
        self.events_repo = events_repo

    async def __call__(self) -> ScheduleEventFull:
        if event := await self.events_repo.get_current_event():
            return event
        raise NoCurrentEvent
