import logging
from dataclasses import dataclass

from fanfan.adapters.config.models import LimitsConfig
from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.adapters.utils.rate_limit import RateLimitFactory
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.schedule.management.common import ANNOUNCE_LIMIT_NAME
from fanfan.core.events.schedule import ScheduleChangedEvent
from fanfan.core.exceptions.limiter import RateLimitCooldown
from fanfan.core.exceptions.schedule import (
    CurrentEventNotAllowed,
    EventNotFound,
    ScheduleEditTooFast,
)
from fanfan.core.models.schedule_change import ScheduleChange, ScheduleChangeType
from fanfan.core.models.schedule_event import ScheduleEvent, ScheduleEventId
from fanfan.core.services.access import UserAccessValidator

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SkipEventResult:
    event: ScheduleEvent


class SkipEvent:
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        limits: LimitsConfig,
        access: UserAccessValidator,
        uow: UnitOfWork,
        rate_limit_factory: RateLimitFactory,
        id_provider: IdProvider,
        events_broker: EventsBroker,
        mailing_repo: MailingRepository,
    ) -> None:
        self.schedule_repo = schedule_repo
        self.limits = limits
        self.access = access
        self.uow = uow
        self.rate_limit_factory = rate_limit_factory
        self.events_broker = events_broker
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo

    async def __call__(self, event_id: ScheduleEventId) -> SkipEventResult:
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
                # Get and check event
                event = await self.schedule_repo.get_event_by_id(event_id)
                if event is None:
                    raise EventNotFound(event_id=event_id)
                if event.is_current is True:
                    raise CurrentEventNotAllowed

                # Get next event at this point
                next_event_before = await self.schedule_repo.get_next_event()

                # Toggle event skip
                event.is_skipped = not event.is_skipped
                await self.schedule_repo.save_event(event)

                next_event_after = await self.schedule_repo.get_next_event()

                schedule_change = ScheduleChange(
                    changed_event_id=event.id,
                    argument_event_id=None,
                    type=ScheduleChangeType.SKIPPED
                    if event.is_skipped
                    else ScheduleChangeType.UNSKIPPED,
                    user_id=user.id,
                    mailing_id=None,
                    send_global_announcement=(next_event_before != next_event_after),
                )
                schedule_change = await self.schedule_repo.add_schedule_change(
                    schedule_change
                )

                # Commit and proceed
                await self.uow.commit()
                await self.events_broker.publish(
                    ScheduleChangedEvent(schedule_change_id=schedule_change.id)
                )

                # Update event after commit
                event = await self.schedule_repo.get_event_by_id(event_id)

                logger.info(
                    "Event %s was skipped by user %s",
                    event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"skipped_event": event},
                )
                return SkipEventResult(
                    event=event,
                )
        except RateLimitCooldown as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
