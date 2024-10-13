from fanfan.core.exceptions.events import NoCurrentEvent
from fanfan.core.models.event import FullEventModel
from fanfan.infrastructure.db.repositories.events import EventsRepository


class GetCurrentEvent:
    def __init__(self, events_repo: EventsRepository) -> None:
        self.events_repo = events_repo

    async def __call__(self) -> FullEventModel:
        if event := await self.events_repo.get_current_event():
            return event
        raise NoCurrentEvent
