from dataclasses import dataclass

from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.models.event import FullEventModel
from fanfan.core.models.page import Page, Pagination


@dataclass(frozen=True, slots=True)
class GetSchedulePageDTO:
    pagination: Pagination | None = None
    search_query: str | None = None


class GetSchedulePage(Interactor[GetSchedulePageDTO, Page[FullEventModel]]):
    def __init__(self, events_repo: EventsRepository, id_provider: IdProvider) -> None:
        self.events_repo = events_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        data: GetSchedulePageDTO,
    ) -> Page[FullEventModel]:
        events = await self.events_repo.list_events(
            search_query=data.search_query,
            pagination=data.pagination,
            user_id=self.id_provider.get_current_user_id(),
        )
        return Page(
            items=events,
            total=await self.events_repo.count_events(data.search_query),
        )
