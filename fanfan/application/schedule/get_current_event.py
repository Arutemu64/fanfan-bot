from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.core.dto.schedule import ScheduleEventDTO


class GetCurrentScheduleEvent:
    def __init__(self, schedule_repo: ScheduleEventsRepository) -> None:
        self.schedule_repo = schedule_repo

    async def __call__(self) -> ScheduleEventDTO | None:
        return await self.schedule_repo.read_current_event()
