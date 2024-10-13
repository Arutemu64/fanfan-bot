from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.events import EventNotFound
from fanfan.core.models.event import EventId, FullEventModel
from fanfan.infrastructure.db.repositories.events import EventsRepository


class GetEventById(Interactor[EventId, FullEventModel]):
    def __init__(self, events_repo: EventsRepository, id_provider: IdProvider) -> None:
        self.events_repo = events_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        event_id: EventId,
    ) -> FullEventModel:
        if event := await self.events_repo.get_event_by_id(
            event_id=event_id, user_id=self.id_provider.get_current_user_id()
        ):
            return event
        raise EventNotFound
