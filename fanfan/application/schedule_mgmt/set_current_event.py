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
from fanfan.core.exceptions.events import AnnounceTooFast
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
class SetCurrentEventResult:
    current_event: EventModel
    mailing_data: MailingData


class SetCurrentEvent(Interactor[EventId | None, SetCurrentEventResult]):
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

    async def __call__(self, event_id: EventId | None) -> SetCurrentEventResult:
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
                # Set as current
                event = await self.events_repo.set_as_current(event_id)
                await self.uow.commit()

                # Send announcements
                mailing_data = await self.notifier.send_announcements(
                    send_global_announcement=True,
                    event_changes=[
                        EventChangeDTO(
                            event=event,
                            type=EventChangeType.SET_AS_CURRENT,
                        )
                        if event
                        else None
                    ],
                )

                logger.info(
                    "Event %s was set as current by user %s",
                    event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"event": event},
                )
                return SetCurrentEventResult(
                    current_event=event,
                    mailing_data=mailing_data,
                )
        except TooFast as e:
            raise AnnounceTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e
