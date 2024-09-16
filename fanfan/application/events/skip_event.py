import logging
import time
from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.events.common import (
    ANNOUNCEMENT_LOCK,
    ANNOUNCEMENT_TIMESTAMP,
    prepare_notifications,
)
from fanfan.core.exceptions.events import (
    AnnounceTooFast,
    CurrentEventNotAllowed,
    EventNotFound,
)
from fanfan.core.models.event import EventDTO
from fanfan.core.models.notification import MailingInfo
from fanfan.infrastructure.db.models import Event, Settings
from fanfan.infrastructure.db.queries.events import next_event_query
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier

logger = logging.getLogger(__name__)


@dataclass
class SkipEventResult:
    event: EventDTO
    mailing_info: MailingInfo


class SkipEvent:
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        notifier: Notifier,
    ) -> None:
        self.session = session
        self.redis = redis
        self.notifier = notifier

    async def __call__(self, event_id: int) -> SkipEventResult:
        async with self.session, self.redis.lock(ANNOUNCEMENT_LOCK, 10):
            # Throttle
            settings = await self.session.get(Settings, 1)
            old_timestamp = float(await self.redis.get(ANNOUNCEMENT_TIMESTAMP) or 0)
            if (time.time() - old_timestamp) < settings.announcement_timeout:
                raise AnnounceTooFast(settings.announcement_timeout, old_timestamp)

            # Get event
            event = await self.session.get(Event, event_id)
            if not event:
                raise EventNotFound(event_id=event_id)

            # Check if event is not current and get next event
            current_event = await self.session.scalar(
                select(Event).where(Event.current.is_(True))
            )
            if event is current_event:
                raise CurrentEventNotAllowed
            next_event = await self.session.scalar(next_event_query())

            # Toggle event skip
            event.skip = not event.skip
            await self.session.flush([event])
            await self.session.refresh(event)

            # Prepare subscriptions
            notifications = await prepare_notifications(
                session=self.session,
                next_event_before=next_event,
                changed_events=[event],
            )

            await self.session.commit()
            await self.redis.set(ANNOUNCEMENT_TIMESTAMP, time.time())
            logger.info("Event %s was skipped", event_id)
            mailing_info = await self.notifier.schedule_mailing(notifications)
            return SkipEventResult(
                event=event.to_dto(),
                mailing_info=mailing_info,
            )
