import logging
from dataclasses import dataclass

from fanfan.adapters.config.models import LimitsConfig
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.adapters.utils.rate_lock import RateLockFactory
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.schedule.management.common import (
    ANNOUNCE_LIMIT_NAME,
)
from fanfan.core.dto.schedule import ScheduleEventDTO
from fanfan.core.events.schedule import ScheduleChanged
from fanfan.core.exceptions.limiter import RateLockCooldown
from fanfan.core.exceptions.schedule import (
    EventNotFound,
    SameEventsAreNotAllowed,
    ScheduleEditTooFast,
)
from fanfan.core.models.schedule_change import (
    ScheduleChangeType,
)
from fanfan.core.models.schedule_event import ScheduleEvent
from fanfan.core.services.schedule import ScheduleService
from fanfan.core.vo.schedule_event import ScheduleEventId

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MoveEventDTO:
    event_id: ScheduleEventId
    place_after_event_id: ScheduleEventId


@dataclass(frozen=True, slots=True)
class MoveScheduleEventResult:
    event: ScheduleEvent
    place_after_event: ScheduleEventDTO


class MoveScheduleEvent:
    def __init__(
        self,
        schedule_repo: ScheduleEventsRepository,
        mailing_repo: MailingDAO,
        limits: LimitsConfig,
        service: ScheduleService,
        uow: UnitOfWork,
        id_provider: IdProvider,
        rate_lock_factory: RateLockFactory,
        events_broker: EventsBroker,
    ) -> None:
        self.schedule_repo = schedule_repo
        self.mailing_repo = mailing_repo
        self.limits = limits
        self.service = service
        self.uow = uow
        self.id_provider = id_provider
        self.rate_lock_factory = rate_lock_factory
        self.events_broker = events_broker

    async def __call__(self, data: MoveEventDTO) -> MoveScheduleEventResult:
        user = await self.id_provider.get_user_data()
        self.service.ensure_user_can_manage_schedule(user)
        lock = self.rate_lock_factory(
            ANNOUNCE_LIMIT_NAME,
            cooldown_period=self.limits.announcement_timeout,
        )
        try:
            async with lock, self.uow:
                # Get and check events
                if data.event_id == data.place_after_event_id:
                    raise SameEventsAreNotAllowed
                event = await self.schedule_repo.get_event_by_id(data.event_id)
                if event is None:
                    raise EventNotFound(event_id=data.event_id)

                place_after_event = await self.schedule_repo.read_event_by_id(
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

                next_event_before_change = await self.schedule_repo.read_next_event()

                # Update event order
                if place_before_event:
                    new_order = (place_after_event.order + place_before_event.order) / 2
                else:
                    new_order = place_after_event.order + 1

                event.order = new_order
                event = await self.schedule_repo.save_event(event)

                next_event_after_change = await self.schedule_repo.read_next_event()

                # Commit and proceed
                await self.uow.commit()
                mailing_id = await self.mailing_repo.create_new_mailing(
                    by_user_id=user.id,
                )
                await self.events_broker.publish(
                    ScheduleChanged(
                        changed_event_id=event.id,
                        argument_event_id=previous_event.id if previous_event else None,
                        type=ScheduleChangeType.MOVED,
                        user_id=user.id,
                        mailing_id=mailing_id,
                        send_global_announcement=(
                            next_event_before_change != next_event_after_change
                        ),
                    )
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
                return MoveScheduleEventResult(
                    event=event,
                    place_after_event=place_after_event,
                )
        except RateLockCooldown as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
