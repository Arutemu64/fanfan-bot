import logging
from dataclasses import dataclass

from fanfan.adapters.config.models import LimitsConfig
from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.adapters.utils.rate_limit import RateLimitFactory
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.schedule.management.common import (
    ANNOUNCE_LIMIT_NAME,
)
from fanfan.core.events.schedule import ScheduleChangedEvent
from fanfan.core.exceptions.limiter import RateLimitCooldown
from fanfan.core.exceptions.schedule import (
    EventNotFound,
    SameEventsAreNotAllowed,
    ScheduleEditTooFast,
)
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeId,
    ScheduleChangeType,
)
from fanfan.core.models.schedule_event import ScheduleEvent, ScheduleEventId
from fanfan.core.services.access import UserAccessValidator

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MoveEventDTO:
    event_id: ScheduleEventId
    place_after_event_id: ScheduleEventId


@dataclass(frozen=True, slots=True)
class MoveEventResult:
    event: ScheduleEvent
    place_after_event: ScheduleEvent
    schedule_change_id: ScheduleChangeId


class MoveEvent:
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        limits: LimitsConfig,
        access: UserAccessValidator,
        uow: UnitOfWork,
        id_provider: IdProvider,
        rate_limit_factory: RateLimitFactory,
        events_broker: EventsBroker,
    ) -> None:
        self.schedule_repo = schedule_repo
        self.limits = limits
        self.access = access
        self.uow = uow
        self.id_provider = id_provider
        self.rate_limit_factory = rate_limit_factory
        self.events_broker = events_broker

    async def __call__(self, data: MoveEventDTO) -> MoveEventResult:
        user = await self.id_provider.get_current_user()
        self.access.ensure_can_edit_schedule(user)
        try:
            async with (
                self.uow,
                self.rate_limit_factory(
                    ANNOUNCE_LIMIT_NAME,
                    cooldown_period=self.limits.announcement_timeout,
                ),
            ):
                # Get and check events
                if data.event_id == data.place_after_event_id:
                    raise SameEventsAreNotAllowed
                event = await self.schedule_repo.get_event_by_id(data.event_id)
                if event is None:
                    raise EventNotFound(event_id=data.event_id)

                place_after_event = await self.schedule_repo.get_event_by_id(
                    data.place_after_event_id
                )
                if place_after_event is None:
                    raise EventNotFound(event_id=data.place_after_event_id)
                place_before_event = await self.schedule_repo.get_next_by_order(
                    place_after_event.order
                )
                previous_event = await self.schedule_repo.get_previous_by_order(
                    event.order
                )

                next_event_before_change = await self.schedule_repo.get_next_event()

                # Update event order
                if place_before_event:
                    event.order = (
                        place_after_event.order + place_before_event.order
                    ) / 2
                else:
                    event.order = place_after_event.order + 1
                await self.schedule_repo.save_event(event)

                next_event_after_change = await self.schedule_repo.get_next_event()

                schedule_change = ScheduleChange(
                    changed_event_id=event.id,
                    argument_event_id=previous_event.id if previous_event else None,
                    type=ScheduleChangeType.MOVED,
                    user_id=user.id,
                    mailing_id=None,
                    send_global_announcement=(
                        next_event_before_change != next_event_after_change
                    ),
                )
                schedule_change = await self.schedule_repo.add_schedule_change(
                    schedule_change
                )

                # Commit and proceed
                await self.uow.commit()
                await self.events_broker.publish(
                    ScheduleChangedEvent(schedule_change_id=schedule_change.id)
                )

                logger.info(
                    "Event %s was placed after event %s by user %s",
                    data.event_id,
                    data.place_after_event_id,
                    self.id_provider.get_current_user_id(),
                    extra={
                        "moved_event": event,
                        "place_after_event": place_after_event,
                    },
                )
                return MoveEventResult(
                    event=event,
                    place_after_event=place_after_event,
                    schedule_change_id=schedule_change.id,
                )
        except RateLimitCooldown as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
