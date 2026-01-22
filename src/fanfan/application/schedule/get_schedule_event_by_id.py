from dataclasses import dataclass

from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.schedule import UserScheduleEventDTO
from fanfan.core.exceptions.schedule import EventNotFound
from fanfan.core.vo.schedule_event import ScheduleEventId


@dataclass(frozen=True, slots=True)
class GetScheduleEventByIdDTO:
    event_id: ScheduleEventId


class GetScheduleEventById:
    def __init__(
        self, schedule_repo: ScheduleEventsRepository, id_provider: IdProvider
    ) -> None:
        self.schedule_repo = schedule_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        data: GetScheduleEventByIdDTO,
    ) -> UserScheduleEventDTO:
        user = await self.id_provider.get_current_user()
        if event := await self.schedule_repo.read_event_user_by_id(
            event_id=data.event_id, user_id=user.id
        ):
            return event
        raise EventNotFound
