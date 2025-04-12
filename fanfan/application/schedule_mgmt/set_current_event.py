import logging
from dataclasses import dataclass

from fanfan.adapters.config.models import LimitsConfig
from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.adapters.utils.limit import LimitFactory
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.schedule_mgmt.common import ANNOUNCE_LIMIT_NAME
from fanfan.core.exceptions.limiter import TooFast
from fanfan.core.exceptions.schedule import EventNotFound, ScheduleEditTooFast
from fanfan.core.models.event import Event, EventId
from fanfan.core.models.schedule_change import ScheduleChange, ScheduleChangeType
from fanfan.core.services.access import AccessService

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SetCurrentEventResult:
    current_event: Event | None


class SetCurrentEvent(Interactor[EventId | None, SetCurrentEventResult]):
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        limits: LimitsConfig,
        access: AccessService,
        uow: UnitOfWork,
        limiter: LimitFactory,
        id_provider: IdProvider,
        events_broker: EventsBroker,
        mailing_repo: MailingRepository,
    ) -> None:
        self.schedule_repo = schedule_repo
        self.limits = limits
        self.access = access
        self.uow = uow
        self.limiter = limiter
        self.events_broker = events_broker
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo

    async def __call__(self, event_id: EventId | None) -> SetCurrentEventResult:
        user = await self.id_provider.get_current_user()
        self.access.ensure_can_edit_schedule(user)
        try:
            async with (
                self.uow,
                self.limiter(
                    ANNOUNCE_LIMIT_NAME,
                    cooldown_period=self.limits.announcement_timeout,
                ),
            ):
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

                # Save schedule change
                schedule_change = ScheduleChange(
                    type=ScheduleChangeType.SET_AS_CURRENT,
                    changed_event_id=event.id if event else None,
                    argument_event_id=previous_current_event.id
                    if previous_current_event
                    else None,
                    user_id=user.id,
                    mailing_id=None,
                    send_global_announcement=True,
                )
                schedule_change = await self.schedule_repo.add_schedule_change(
                    schedule_change
                )

                # Commit and publish
                await self.uow.commit()
                await self.events_broker.schedule_changed(schedule_change)

                logger.info(
                    "Event %s was set as current by user %s",
                    event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"current_event": event},
                )
                return SetCurrentEventResult(
                    current_event=event,
                )
        except TooFast as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
