import math
from typing import Optional

from fanfan.application.dto.common import Page
from fanfan.application.dto.event import ScheduleEventDTO
from fanfan.application.exceptions.event import EventNotFound
from fanfan.application.services.base import BaseService


class ScheduleService(BaseService):
    async def get_schedule_page(
        self,
        page: int,
        events_per_page: int,
        search_query: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Page[ScheduleEventDTO]:
        """
        Get a page of events
        @param page: Page
        @param events_per_page: Events per page
        @param search_query: User's string search query
        (search among event titles and nominations)
        @param user_id: If provided, every ScheduleEventDTO will also
        include user's SubscriptionDTO
        @return:
        """
        events = await self.uow.events.paginate_events(
            page=page,
            events_per_page=events_per_page,
            search_query=search_query,
            user_id=user_id,
        )
        events_count = await self.uow.events.count_events(search_query)
        total = math.ceil(events_count / events_per_page)
        return Page(
            items=[e.to_schedule_dto() for e in events],
            number=page,
            total=total if total > 0 else 1,
        )

    async def get_page_number_by_event(
        self, event_id: int, events_per_page: int, search_query: Optional[str] = None
    ) -> int:
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound
        return await self.uow.events.get_page_number_by_event(
            event_id=event_id,
            events_per_page=events_per_page,
            search_query=search_query,
        )
