import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.common.limiter import Limiter
from fanfan.application.common.notifier import Notifier
from fanfan.application.schedule_mgmt.common import (
    ANNOUNCE_LIMIT_NAME,
)
from fanfan.core.exceptions.events import (
    AnnounceTooFast,
    EventNotFound,
    SameEventsAreNotAllowed,
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


@dataclass(frozen=True, slots=True)
class MoveEventDTO:
    event_id: EventId
    after_event_id: EventId


@dataclass(frozen=True, slots=True)
class MoveEventResult:
    event: EventModel
    after_event: EventModel
    mailing_data: MailingData


class MoveEvent(Interactor[MoveEventDTO, MoveEventResult]):
    def __init__(
        self,
        events_repo: EventsRepository,
        settings_repo: SettingsRepository,
        access: AccessService,
        uow: UnitOfWork,
        id_provider: IdProvider,
        limiter: Limiter,
        notifier: Notifier,
    ) -> None:
        self.events_repo = events_repo
        self.settings_repo = settings_repo
        self.access = access
        self.uow = uow
        self.id_provider = id_provider
        self.limiter = limiter
        self.notifier = notifier

    async def __call__(self, data: MoveEventDTO) -> MoveEventResult:
        user = await self.id_provider.get_current_user()
        await self.access.ensure_can_edit_schedule(user)
        settings = await self.settings_repo.get_settings()
        try:
            async with (
                self.uow,
                self.limiter(
                    ANNOUNCE_LIMIT_NAME,
                    limit_timeout=settings.announcement_timeout,
                ),
            ):
                # Check event
                if data.event_id == data.after_event_id:
                    raise SameEventsAreNotAllowed

                # Get event and after_event
                after_event = await self.events_repo.get_event_by_id(
                    data.after_event_id
                )
                if after_event is None:
                    raise EventNotFound(event_id=data.after_event_id)

                # Get before_event
                before_event = await self.events_repo.get_next_by_order(
                    after_event.order
                )

                # Get next event at this point
                next_event_before = await self.events_repo.get_next_event()

                # Update event order
                if before_event:
                    order = (after_event.order + before_event.order) / 2
                else:
                    order = after_event.order + 1
                event = await self.events_repo.set_order(data.event_id, order)
                await self.uow.commit()

                # Send announcements
                next_event_after = await self.events_repo.get_next_event()
                mailing_data = await self.notifier.send_announcements(
                    send_global_announcement=next_event_before.id
                    != next_event_after.id,
                    event_changes=[
                        EventChangeDTO(event=event, type=EventChangeType.MOVE)
                    ],
                )
                logger.info(
                    "Event %s was placed after event %s by user %s",
                    data.event_id,
                    data.after_event_id,
                    self.id_provider.get_current_user_id(),
                    extra={"event": event, "after_event": after_event},
                )
                return MoveEventResult(
                    event=event,
                    after_event=after_event,
                    mailing_data=mailing_data,
                )
        except TooFast as e:
            raise AnnounceTooFast(
                announcement_timeout=e.limit_timeout, old_timestamp=e.current_timestamp
            ) from e