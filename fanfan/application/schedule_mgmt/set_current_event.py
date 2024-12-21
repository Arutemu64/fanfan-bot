import logging
from dataclasses import dataclass

from fanfan.adapters.config.models import LimitsConfig
from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.limit import LimitFactory
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.schedule_mgmt.common import ANNOUNCE_LIMIT_NAME
from fanfan.core.exceptions.events import EventNotFound, ScheduleEditTooFast
from fanfan.core.exceptions.limiter import TooFast
from fanfan.core.models.event import Event, EventId
from fanfan.core.models.mailing import MailingId
from fanfan.core.services.access import AccessService
from fanfan.presentation.stream.routes.notifications.send_announcements import (
    EventChangeDTO,
    EventChangeType,
    SendAnnouncementsDTO,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SetCurrentEventResult:
    current_event: Event | None
    mailing_id: MailingId | None


class SetCurrentEvent(Interactor[EventId | None, SetCurrentEventResult]):
    def __init__(
        self,
        events_repo: EventsRepository,
        limits: LimitsConfig,
        access: AccessService,
        uow: UnitOfWork,
        limiter: LimitFactory,
        id_provider: IdProvider,
        stream_broker_adapter: StreamBrokerAdapter,
        mailing_repo: MailingRepository,
    ) -> None:
        self.events_repo = events_repo
        self.limits = limits
        self.access = access
        self.uow = uow
        self.limiter = limiter
        self.stream_broker_adapter = stream_broker_adapter
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo

    async def __call__(self, event_id: EventId | None) -> SetCurrentEventResult:
        user = await self.id_provider.get_current_user()
        await self.access.ensure_can_edit_schedule(user)
        try:
            async with (
                self.uow,
                self.limiter(
                    ANNOUNCE_LIMIT_NAME,
                    cooldown_period=self.limits.announcement_timeout,
                ),
            ):
                # Unset current event
                if current_event := await self.events_repo.get_current_event():
                    current_event.is_current = None
                    await self.events_repo.save_event(current_event)

                # Get event and set as current
                if event_id is not None:
                    event = await self.events_repo.get_event_by_id(event_id)
                    if event is None:
                        raise EventNotFound(event_id)
                    event.is_current = True
                    await self.events_repo.save_event(event)
                else:
                    event = None

                await self.uow.commit()

                # Send announcements
                if event:
                    mailing_id = await self.mailing_repo.create_new_mailing(
                        by_user_id=self.id_provider.get_current_user_id()
                    )
                    await self.stream_broker_adapter.send_announcements(
                        SendAnnouncementsDTO(
                            send_global_announcement=True,
                            event_changes=[
                                EventChangeDTO(
                                    event=event,
                                    type=EventChangeType.SET_AS_CURRENT,
                                )
                            ],
                            mailing_id=mailing_id,
                        )
                    )
                else:
                    mailing_id = None

                logger.info(
                    "Event %s was set as current by user %s",
                    event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"current_event": event},
                )
                return SetCurrentEventResult(
                    current_event=event,
                    mailing_id=mailing_id,
                )
        except TooFast as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
