from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.schedule import EventNotFound
from fanfan.core.models.event import EventFull, EventId


class GetEventById:
    def __init__(
        self, events_repo: ScheduleRepository, id_provider: IdProvider
    ) -> None:
        self.events_repo = events_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        event_id: EventId,
    ) -> EventFull:
        if event := await self.events_repo.get_event_by_id(
            event_id=event_id, user_id=self.id_provider.get_current_user_id()
        ):
            return event
        raise EventNotFound
