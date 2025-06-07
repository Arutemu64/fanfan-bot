import logging
from dataclasses import dataclass

from fanfan.adapters.config.models import LimitsConfig
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.adapters.utils.rate_lock import RateLockFactory
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.schedule.management.common import ANNOUNCE_LIMIT_NAME
from fanfan.core.events.schedule import ScheduleChanged
from fanfan.core.exceptions.limiter import RateLockCooldown
from fanfan.core.exceptions.schedule import EventNotFound, ScheduleEditTooFast
from fanfan.core.models.schedule_change import ScheduleChangeType
from fanfan.core.models.schedule_event import ScheduleEvent
from fanfan.core.services.schedule import ScheduleService
from fanfan.core.vo.schedule_event import ScheduleEventId

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SetCurrentScheduleEventResult:
    current_event: ScheduleEvent | None


class SetCurrentScheduleEvent:
    def __init__(
        self,
        schedule_repo: ScheduleEventsRepository,
        limits: LimitsConfig,
        service: ScheduleService,
        uow: UnitOfWork,
        rate_lock_factory: RateLockFactory,
        id_provider: IdProvider,
        events_broker: EventsBroker,
        mailing_repo: MailingDAO,
    ) -> None:
        self.schedule_repo = schedule_repo
        self.limits = limits
        self.service = service
        self.uow = uow
        self.rate_lock_factory = rate_lock_factory
        self.events_broker = events_broker
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo

    async def __call__(
        self, event_id: ScheduleEventId | None
    ) -> SetCurrentScheduleEventResult:
        user = await self.id_provider.get_user_data()
        self.service.ensure_user_can_manage_schedule(user)
        lock = self.rate_lock_factory(
            ANNOUNCE_LIMIT_NAME,
            cooldown_period=self.limits.announcement_timeout,
        )
        try:
            async with self.uow, lock:
                # Unset current event
                previous_current_event = await self.schedule_repo.get_current_event()
                if previous_current_event:
                    previous_current_event.is_current = None
                    await self.schedule_repo.save_event(previous_current_event)

                # Get event and set as current
                if event_id is not None:
                    event = await self.schedule_repo.get_event_by_id(event_id)
                    if event is None:
                        raise EventNotFound(event_id)
                    event.is_current = True
                    await self.schedule_repo.save_event(event)
                else:
                    event = None

                # Commit and publish
                await self.uow.commit()
                if event_id is not None:
                    mailing_id = await self.mailing_repo.create_new_mailing(
                        by_user_id=user.id,
                    )
                    await self.events_broker.publish(
                        ScheduleChanged(
                            type=ScheduleChangeType.SET_AS_CURRENT,
                            changed_event_id=event.id if event else None,
                            argument_event_id=previous_current_event.id
                            if previous_current_event
                            else None,
                            user_id=user.id,
                            mailing_id=mailing_id,
                            send_global_announcement=True,
                        )
                    )

                logger.info(
                    "Event %s was set as current by user %s",
                    event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"current_event": event},
                )
                return SetCurrentScheduleEventResult(
                    current_event=event,
                )
        except RateLockCooldown as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
