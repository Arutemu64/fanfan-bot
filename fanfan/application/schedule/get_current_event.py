from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.core.dto.schedule import ScheduleEventDTO
from fanfan.core.exceptions.schedule import NoCurrentEvent


class GetCurrentEvent:
    def __init__(self, schedule_repo: ScheduleRepository) -> None:
        self.schedule_repo = schedule_repo

    async def __call__(self) -> ScheduleEventDTO:
        if event := await self.schedule_repo.read_current_event():
            return event
        raise NoCurrentEvent
