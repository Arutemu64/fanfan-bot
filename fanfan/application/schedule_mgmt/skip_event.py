import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.common.limiter import Limiter
from fanfan.application.common.notifier import Notifier
from fanfan.application.schedule_mgmt.common import ANNOUNCE_LIMIT_NAME
from fanfan.core.exceptions.events import (
    AnnounceTooFast,
    EventNotFound,
)
from fanfan.core.exceptions.limiter import TooFast
from fanfan.core.models.event import EventId, EventModel
from fanfan.core.models.mailing import MailingData
from fanfan.core.services.access import AccessService
from fanfan.presentation.stream.routes.prepare_announcements import (
    EventChangeDTO,
    EventChangeType,
)

logger = logging.getLogger(__name__)


@dataclass
class SkipEventResult:
    event: EventModel
    mailing_data: MailingData


class SkipEvent(Interactor[EventId, SkipEventResult]):
    def __init__(
        self,
        events_repo: EventsRepository,
        settings_repo: SettingsRepository,
        access: AccessService,
        uow: UnitOfWork,
        limiter: Limiter,
        notifier: Notifier,
        id_provider: IdProvider,
    ) -> None:
        self.events_repo = events_repo
        self.settings_repo = settings_repo
        self.access = access
        self.uow = uow
        self.limiter = limiter
        self.notifier = notifier
        self.id_provider = id_provider

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

                # Get next event at this point
                next_event_before = await self.events_repo.get_next_event()

                # Toggle event skip
                event = await self.events_repo.set_skip(event_id, not event.skip)
                await self.uow.commit()

                # Send announcements
                next_event_after = await self.events_repo.get_next_event()
                change_type = (
                    EventChangeType.SKIP if event.skip else EventChangeType.UNSKIP
                )
                mailing_data = await self.notifier.send_announcements(
                    send_global_announcement=next_event_before.id
                    != next_event_after.id,
                    event_changes=[EventChangeDTO(event=event, type=change_type)],
                )
                logger.info(
                    "Event %s was skipped by user %s",
                    event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"event": event},
                )
                return SkipEventResult(
                    event=event,
                    mailing_data=mailing_data,
                )
        except TooFast as e:
            raise AnnounceTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
