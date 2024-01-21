from fanfan.application.dto.event import FullEventDTO
from fanfan.application.exceptions.event import (
    NoCurrentEvent,
)
from fanfan.application.services.base import BaseService


class EventService(BaseService):
    async def get_current_event(self) -> FullEventDTO:
        """
        Get current event
        @return:
        """
        if event := await self.uow.events.get_current_event():
            return event.to_dto()
        raise NoCurrentEvent
