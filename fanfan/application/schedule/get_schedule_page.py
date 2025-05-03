from dataclasses import dataclass

from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.schedule_event import ScheduleEventFull


@dataclass(frozen=True, slots=True)
class GetSchedulePageDTO:
    pagination: Pagination | None = None
    search_query: str | None = None


class GetSchedulePage:
    def __init__(
        self, events_repo: ScheduleRepository, id_provider: IdProvider
    ) -> None:
        self.events_repo = events_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        data: GetSchedulePageDTO,
    ) -> Page[ScheduleEventFull]:
        events = await self.events_repo.read_events_list_for_user(
            user_id=self.id_provider.get_current_user_id(),
            search_query=data.search_query,
            pagination=data.pagination,
        )
        return Page(
            items=events,
            total=await self.events_repo.count_events(data.search_query),
        )
