import logging
import time
from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.schedule_mgmt.common import (
    ANNOUNCEMENT_LOCK,
    ANNOUNCEMENT_TIMESTAMP,
)
from fanfan.application.schedule_mgmt.utils.prepare_notifications import (
    EventChangeDTO,
    EventChangeType,
    PrepareNotifications,
)
from fanfan.core.exceptions.events import (
    AnnounceTooFast,
    CurrentEventNotAllowed,
    EventNotFound,
    SkippedEventNotAllowed,
)
from fanfan.core.models.event import EventDTO
from fanfan.core.models.notification import MailingInfo
from fanfan.infrastructure.db.models import Event, Settings
from fanfan.infrastructure.db.queries.events import next_event_query
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier

logger = logging.getLogger(__name__)


@dataclass
class SetCurrentEventResult:
    current_event: EventDTO
    mailing_info: MailingInfo


class SetCurrentEvent:
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        prepare_notifications: PrepareNotifications,
        notifier: Notifier,
        id_provider: IdProvider,
    ) -> None:
        self.session = session
        self.redis = redis
        self.prepare_notifications = prepare_notifications
        self.notifier = notifier
        self.id_provider = id_provider

    async def __call__(self, event_id: int | None) -> SetCurrentEventResult:
        async with self.session, self.redis.lock(ANNOUNCEMENT_LOCK, 10):
            # Throttle
            settings = await self.session.get(Settings, 1)
            old_timestamp = float(await self.redis.get(ANNOUNCEMENT_TIMESTAMP) or 0)
            if (time.time() - old_timestamp) < settings.announcement_timeout:
                raise AnnounceTooFast(settings.announcement_timeout, old_timestamp)

            # Unmark current event if present
            current_event = await self.session.scalar(
                select(Event).where(Event.current.is_(True))
            )
            next_event = await self.session.scalar(next_event_query())
            if current_event:
                current_event.current = None
                await self.session.flush([current_event])

            if isinstance(event_id, int):
                event = await self.session.get(Event, event_id)
                if not event:
                    raise EventNotFound(event_id=event_id)
                if event.skip:
                    raise SkippedEventNotAllowed
                if event is current_event:
                    raise CurrentEventNotAllowed
                event.current = True
                await self.session.flush([event])
            else:
                event = None

            # Prepare subscriptions
            notifications = await self.prepare_notifications(
                session=self.session,
                next_event_before=next_event,
                event_changes=[
                    EventChangeDTO(event, EventChangeType.SET_AS_CURRENT)
                    if isinstance(event, Event)
                    else None
                ],
            )

            await self.session.commit()
            await self.redis.set(ANNOUNCEMENT_TIMESTAMP, time.time())
            logger.info(
                "Event %s was set as current by user %s",
                event_id,
                self.id_provider.get_current_user_id(),
            )
            mailing_info = await self.notifier.schedule_mailing(notifications)
            return SetCurrentEventResult(
                current_event=event.to_dto() if event else None,
                mailing_info=mailing_info,
            )
