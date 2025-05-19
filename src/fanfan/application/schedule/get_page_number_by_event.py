from dataclasses import dataclass

from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.core.vo.schedule_event import ScheduleEventId


@dataclass(frozen=True, slots=True)
class GetPageNumberByEventDTO:
    event_id: ScheduleEventId
    events_per_page: int


class GetPageNumberByScheduleEvent:
    def __init__(self, schedule_repo: ScheduleEventsRepository) -> None:
        self.schedule_repo = schedule_repo

    async def __call__(
        self,
        data: GetPageNumberByEventDTO,
    ) -> int | None:
        return await self.schedule_repo.get_page_number_by_event(
            data.event_id, data.events_per_page
        )
