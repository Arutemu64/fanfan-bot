from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.core.exceptions.events import NoCurrentEvent
from fanfan.core.models.event import FullEvent


class GetCurrentEvent:
    def __init__(self, events_repo: EventsRepository) -> None:
        self.events_repo = events_repo

    async def __call__(self) -> FullEvent:
        if event := await self.events_repo.get_current_event():
            return event
        raise NoCurrentEvent
