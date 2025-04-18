from dataclasses import dataclass

from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.core.models.event import EventId


@dataclass(frozen=True, slots=True)
class GetPageNumberByEventDTO:
    event_id: EventId
    events_per_page: int


class GetPageNumberByEvent:
    def __init__(self, events_repo: ScheduleRepository) -> None:
        self.events_repo = events_repo

    async def __call__(
        self,
        data: GetPageNumberByEventDTO,
    ) -> int | None:
        return await self.events_repo.get_page_number_by_event(
            data.event_id, data.events_per_page
        )
