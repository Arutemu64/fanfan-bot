import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.announcer import Announcer
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
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
        access: AccessService,
        uow: UnitOfWork,
        announcer: Announcer,
        id_provider: IdProvider,
    ) -> None:
        self.events_repo = events_repo
        self.access = access
        self.uow = uow
        self.announcer = announcer
        self.id_provider = id_provider

    async def __call__(self, event_id: EventId | None) -> SetCurrentEventResult:
        user = await self.id_provider.get_current_user()
        await self.access.ensure_can_edit_schedule(user)
        async with self.uow, self.announcer:
            # Set as current
            event = await self.events_repo.set_as_current(event_id)
            await self.uow.commit()

            # Send announcements
            mailing_data = await self.announcer.send_announcements(
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
