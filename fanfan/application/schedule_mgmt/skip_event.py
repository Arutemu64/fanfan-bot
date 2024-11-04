import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.limiter import Limiter
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.schedule_mgmt.common import ANNOUNCE_LIMIT_NAME
from fanfan.core.dto.mailing import MailingId
from fanfan.core.exceptions.events import (
    CurrentEventNotAllowed,
    EventNotFound,
    ScheduleEditTooFast,
)
from fanfan.core.exceptions.limiter import TooFast
from fanfan.core.models.event import EventId, EventModel
from fanfan.core.services.access import AccessService
from fanfan.presentation.stream.routes.notifications.send_announcements import (
    EventChangeDTO,
    EventChangeType,
    SendAnnouncementsDTO,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SkipEventResult:
    event: EventModel
    mailing_id: MailingId


class SkipEvent(Interactor[EventId, SkipEventResult]):
    def __init__(
        self,
        events_repo: EventsRepository,
        settings_repo: SettingsRepository,
        access: AccessService,
        uow: UnitOfWork,
        limiter: Limiter,
        id_provider: IdProvider,
        stream_broker_adapter: StreamBrokerAdapter,
        mailing_repo: MailingRepository,
    ) -> None:
        self.events_repo = events_repo
        self.settings_repo = settings_repo
        self.access = access
        self.uow = uow
        self.limiter = limiter
        self.stream_broker_adapter = stream_broker_adapter
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo

    async def __call__(self, event_id: EventId) -> SkipEventResult:
        user = await self.id_provider.get_current_user()
        await self.access.ensure_can_edit_schedule(user)
        settings = await self.settings_repo.get_settings()
        try:
            async with (
                self.uow,
                self.limiter(
                    ANNOUNCE_LIMIT_NAME, limit_timeout=settings.announcement_timeout
                ),
            ):
                # Get event
                event = await self.events_repo.get_event_by_id(event_id)
                if event is None:
                    raise EventNotFound(event_id=event_id)
                if event.current is True:
                    raise CurrentEventNotAllowed

                # Get next event at this point
                next_event_before = await self.events_repo.get_next_event()

                # Toggle event skip
                event.skip = not event.skip
                await self.events_repo.save_event(event)
                await self.uow.commit()

                # Update event after commit
                event = await self.events_repo.get_event_by_id(event_id)

                # Check if we should send global announcement
                next_event_after = await self.events_repo.get_next_event()
                if next_event_before and next_event_after:
                    send_global_announcement = (
                        next_event_before.id != next_event_after.id
                    )
                else:
                    send_global_announcement = False

                # Send mailing
                mailing_id = await self.mailing_repo.create_new_mailing(
                    by_user_id=self.id_provider.get_current_user_id()
                )
                await self.stream_broker_adapter.send_announcements(
                    SendAnnouncementsDTO(
                        send_global_announcement=send_global_announcement,
                        event_changes=[
                            EventChangeDTO(
                                event=event,
                                type=EventChangeType.SKIP
                                if event.skip
                                else EventChangeType.UNSKIP,
                            )
                        ],
                        mailing_id=mailing_id,
                    )
                )
                logger.info(
                    "Event %s was skipped by user %s",
                    event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"skipped_event": event},
                )
                return SkipEventResult(
                    event=event,
                    mailing_id=mailing_id,
                )
        except TooFast as e:
            raise ScheduleEditTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
