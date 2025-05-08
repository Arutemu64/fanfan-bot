from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.schedule import ScheduleEventUserDTO
from fanfan.core.exceptions.schedule import EventNotFound
from fanfan.core.models.schedule_event import ScheduleEventId


class GetEventForUser:
    def __init__(
        self, schedule_repo: ScheduleRepository, id_provider: IdProvider
    ) -> None:
        self.schedule_repo = schedule_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        event_id: ScheduleEventId,
    ) -> ScheduleEventUserDTO:
        if event := await self.schedule_repo.read_event_for_user(
            event_id=event_id, user_id=self.id_provider.get_current_user_id()
        ):
            return event
        raise EventNotFound
