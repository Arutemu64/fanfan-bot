from fanfan.application.dto.event import EventDTO
from fanfan.application.exceptions.event import (
    EventNotFound,
    NoCurrentEvent,
)
from fanfan.application.services.base import BaseService


class EventService(BaseService):
    async def get_event(self, event_id: int) -> EventDTO:
        """
        @param event_id:
        @raise EventNotFound
        @return:
        """
        if event := await self.uow.events.get_event(event_id):
            return event.to_dto()
        raise EventNotFound

    async def get_current_event(self) -> EventDTO:
        """
        Get current event
        @raise NoCurrentEvent
        @return:
        """
        if event := await self.uow.events.get_current_event():
            return event.to_dto()
        raise NoCurrentEvent
