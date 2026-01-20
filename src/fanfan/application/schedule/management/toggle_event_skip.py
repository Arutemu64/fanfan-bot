import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.app_settings import SettingsRepository
from fanfan.adapters.db.repositories.schedule_changes import ScheduleChangesRepository
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.nats.events_broker import EventsBroker
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.adapters.redis.rate_lock import RateLockFactory
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.schedule.management.common import ANNOUNCE_LIMIT_NAME
from fanfan.core.events.schedule import NewScheduleChange
from fanfan.core.exceptions.limiter import RateLockCooldown
from fanfan.core.exceptions.schedule import (
    CurrentEventNotAllowed,
    EventNotFound,
    ScheduleEditTooFast,
)
from fanfan.core.models.schedule_change import ScheduleChange, ScheduleChangeType
from fanfan.core.models.schedule_event import ScheduleEvent
from fanfan.core.services.schedule import ScheduleService
from fanfan.core.vo.schedule_event import ScheduleEventId

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ToggleScheduleEventSkipDTO:
    event_id: ScheduleEventId


@dataclass(slots=True, frozen=True)
class ToggleScheduleEventSkipResult:
    event: ScheduleEvent


class ToggleScheduleEventSkip:
    def __init__(
        self,
        schedule_repo: ScheduleEventsRepository,
        settings_repo: SettingsRepository,
        changes_repo: ScheduleChangesRepository,
        service: ScheduleService,
        uow: UnitOfWork,
        rate_lock_factory: RateLockFactory,
        id_provider: IdProvider,
        events_broker: EventsBroker,
        mailing_repo: MailingDAO,
    ) -> None:
        self.schedule_repo = schedule_repo
        self.settings_repo = settings_repo
        self.changes_repo = changes_repo
        self.service = service
        self.uow = uow
        self.rate_lock_factory = rate_lock_factory
        self.events_broker = events_broker
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo

    async def __call__(
        self, data: ToggleScheduleEventSkipDTO
    ) -> ToggleScheduleEventSkipResult:
        user = await self.id_provider.get_current_user()
        await self.service.ensure_user_can_manage_schedule(user)

        settings = await self.settings_repo.get_settings()
        lock = self.rate_lock_factory(
            ANNOUNCE_LIMIT_NAME,
            cooldown_period=settings.limits.announcement_timeout,
        )

        try:
            async with self.uow, lock:
                # Get and check event
                event = await self.schedule_repo.get_event_by_id(data.event_id)
                if event is None:
                    raise EventNotFound(event_id=data.event_id)
                if event.is_current:
                    raise CurrentEventNotAllowed

                # Get next event at this point
                next_event_before = await self.schedule_repo.read_next_event()

                # Toggle event skip
                event.is_skipped = not event.is_skipped
                await self.schedule_repo.save_event(event)

                next_event_after = await self.schedule_repo.read_next_event()

                # Save schedule change
                mailing_id = await self.mailing_repo.create_new_mailing(
                    by_user_id=user.id
                )
                schedule_change = ScheduleChange(
                    type=ScheduleChangeType.SKIPPED
                    if event.is_skipped
                    else ScheduleChangeType.UNSKIPPED,
                    changed_event_id=event.id,
                    argument_event_id=None,
                    mailing_id=mailing_id,
                    user_id=user.id,
                    send_global_announcement=(next_event_before != next_event_after),
                )
                schedule_change = await self.changes_repo.add_schedule_change(
                    schedule_change
                )

                # Commit and proceed
                await self.uow.commit()
                await self.events_broker.publish(
                    NewScheduleChange(schedule_change_id=schedule_change.id)
                )

                # Update event after commit
                event = await self.schedule_repo.get_event_by_id(data.event_id)

                logger.info(
                    "Event %s was skipped by user %s",
                    data.event_id,
                    user.id,
                    extra={"skipped_event": event},
                )
                return ToggleScheduleEventSkipResult(
                    event=event,
                )
        except RateLockCooldown as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
