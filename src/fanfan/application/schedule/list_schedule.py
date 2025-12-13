from dataclasses import dataclass

from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.schedule import ScheduleEventUserDTO


@dataclass(frozen=True, slots=True)
class ListScheduleDTO:
    pagination: Pagination | None = None
    search_query: str | None = None


class ListSchedule:
    def __init__(
        self, schedule_repo: ScheduleEventsRepository, id_provider: IdProvider
    ) -> None:
        self.schedule_repo = schedule_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        data: ListScheduleDTO,
    ) -> Page[ScheduleEventUserDTO]:
        user = await self.id_provider.get_current_user()
        events = await self.schedule_repo.list_schedule_for_user(
            user_id=user.id,
            search_query=data.search_query,
            pagination=data.pagination,
        )
        return Page(
            items=events,
            total=await self.schedule_repo.count_events(data.search_query),
        )
