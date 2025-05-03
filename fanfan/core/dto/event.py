from dataclasses import dataclass

from fanfan.core.models.block import ScheduleBlock
from fanfan.core.models.nomination import Nomination
from fanfan.core.models.schedule_event import ScheduleEventId
from fanfan.core.models.subscription import Subscription


@dataclass
class UserEventDTO:
    id: ScheduleEventId
    title: str
    is_current: bool | None
    is_skipped: bool
    queue: int | None
    nomination: Nomination | None
    block: ScheduleBlock | None
    subscription: Subscription | None
