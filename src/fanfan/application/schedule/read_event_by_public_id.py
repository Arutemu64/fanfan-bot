from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.schedule import ScheduleEventDTO
from fanfan.core.exceptions.schedule import EventNotFound
from fanfan.core.vo.schedule_event import ScheduleEventPublicId


class ReadScheduleEventByPublicId:
    def __init__(
        self, schedule_repo: ScheduleEventsRepository, id_provider: IdProvider
    ) -> None:
        self.schedule_repo = schedule_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        public_event_id: ScheduleEventPublicId,
    ) -> ScheduleEventDTO:
        if event := await self.schedule_repo.read_event_by_public_id(public_event_id):
            return event
        raise EventNotFound
