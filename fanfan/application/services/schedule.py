from typing import Optional

from fanfan.application.dto.common import Page
from fanfan.application.dto.event import EventDTO, ScheduleEventDTO
from fanfan.application.exceptions.event import (
    EventNotFound,
    NoCurrentEvent,
)
from fanfan.application.services.base import BaseService


class ScheduleService(BaseService):
    async def get_event(self, event_id: int) -> EventDTO:
        """@param event_id:
        @raise EventNotFound
        @return:
        """
        if event := await self.uow.events.get_event(event_id):
            return event.to_dto()
        raise EventNotFound(event_id=event_id)

    async def get_current_event(self) -> EventDTO:
        """Get current event
        @raise NoCurrentEvent
        @return:
        """
        if event := await self.uow.events.get_current_event():
            return event.to_dto()
        raise NoCurrentEvent

    async def get_schedule_page(
        self,
        page_number: int,
        events_per_page: int,
        search_query: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Page[ScheduleEventDTO]:
        """Get a page of schedule
        @param page_number: Page page_number
        @param events_per_page: Events per page
        @param search_query: User's string search query
        (search among event titles and nominations)
        @param user_id: If provided, every ScheduleEventDTO will also
        include user's SubscriptionDTO
        @return:
        """
        page = await self.uow.events.paginate_events(
            page_number=page_number,
            events_per_page=events_per_page,
            search_query=search_query,
            user_id=user_id,
        )
        return Page(
            items=[e.to_schedule_dto() for e in page.items],
            number=page.number,
            total_pages=page.total_pages if page.total_pages > 0 else 1,
        )

    async def get_page_number_by_event(
        self,
        event_id: int,
        events_per_page: int,
        search_query: Optional[str] = None,
    ) -> int:
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound(event_id=event_id)
        return await self.uow.events.get_page_number_by_event(
            event_id=event_id,
            events_per_page=events_per_page,
            search_query=search_query,
        )
