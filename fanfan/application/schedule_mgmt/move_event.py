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
    EventNotFound,
    SameEventsAreNotAllowed,
)
from fanfan.core.models.event import EventDTO
from fanfan.core.models.notification import MailingInfo
from fanfan.infrastructure.db.models import Event, Settings
from fanfan.infrastructure.db.queries.events import next_event_query
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier

logger = logging.getLogger(__name__)


@dataclass
class MoveEventResult:
    event: EventDTO
    after_event: EventDTO
    mailing_info: MailingInfo


class MoveEvent:
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        id_provider: IdProvider,
        prepare_notifications: PrepareNotifications,
        notifier: Notifier,
    ) -> None:
        self.session = session
        self.redis = redis
        self.id_provider = id_provider
        self.prepare_notifications = prepare_notifications
        self.notifier = notifier

    async def __call__(self, event_id: int, after_event_id: int) -> MoveEventResult:
        async with self.session, self.redis.lock(ANNOUNCEMENT_LOCK, 10):
            # Throttle
            settings = await self.session.get(Settings, 1)
            old_timestamp = float(await self.redis.get(ANNOUNCEMENT_TIMESTAMP) or 0)
            if (time.time() - old_timestamp) < settings.announcement_timeout:
                raise AnnounceTooFast(settings.announcement_timeout, old_timestamp)

            if event_id == after_event_id:
                raise SameEventsAreNotAllowed

            # Get event and after_event
            event = await self.session.get(Event, event_id)
            if not event:
                raise EventNotFound(event_id=event_id)
            after_event = await self.session.get(Event, after_event_id)
            if not after_event:
                raise EventNotFound(event_id=after_event_id)

            # Get next event at this point
            next_event = await self.session.scalar(next_event_query())

            # Get before_event
            before_event = await self.session.scalar(
                select(Event)
                .order_by(Event.order)
                .where(Event.order > after_event.order)
                .limit(1)
            )

            # Update event order
            if before_event:
                event.order = (after_event.order + before_event.order) / 2
            else:
                event.order = after_event.order + 1
            await self.session.flush([event])
            await self.session.refresh(event)

            # Prepare notifications
            notifications = await self.prepare_notifications(
                session=self.session,
                next_event_before=next_event,
                event_changes=[EventChangeDTO(event, EventChangeType.MOVE)],
            )

            # Commit
            await self.session.commit()
            await self.redis.set(ANNOUNCEMENT_TIMESTAMP, time.time())
            logger.info(
                "Event %s was placed after event %s",
                event_id,
                after_event_id,
            )

            mailing_info = await self.notifier.schedule_mailing(notifications)

            return MoveEventResult(
                event=event.to_dto(),
                after_event=event.to_dto(),
                mailing_info=mailing_info,
            )
