import logging
import time
from datetime import datetime
from typing import List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader
from pytz import timezone

from fanfan.application.dto.event import EventDTO
from fanfan.application.dto.notification import DeliveryInfo, UserNotification
from fanfan.application.exceptions.event import (
    AnnounceTooFast,
    CurrentEventNotAllowed,
    EventNotFound,
    NoNextEvent,
    SameEventsAreNotAllowed,
    SkippedEventNotAllowed,
)
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.application.services.notification import NotificationService
from fanfan.common.enums import UserRole
from fanfan.config import get_config
from fanfan.infrastructure.db.models import Event
from fanfan.presentation.tgbot import JINJA_TEMPLATES_DIR

logger = logging.getLogger(__name__)

templateLoader = FileSystemLoader(searchpath=JINJA_TEMPLATES_DIR)
jinja = Environment(
    lstrip_blocks=True,
    trim_blocks=True,
    loader=templateLoader,
    enable_async=True,
)
subscription_template = jinja.get_template("subscription_notification.jinja2")
global_announcement_template = jinja.get_template("global_announcement.jinja2")


class ScheduleManagementService(BaseService):
    async def _throttle_global_announcement(self) -> None:
        settings = await self.uow.settings.get_settings()
        timestamp = time.time()
        if (
            timestamp - settings.announcement_timestamp
        ) < settings.announcement_timeout:
            raise AnnounceTooFast(
                settings.announcement_timeout,
                int(
                    settings.announcement_timestamp
                    + settings.announcement_timeout
                    - timestamp,
                ),
            )
        else:
            settings.announcement_timestamp = timestamp

    async def _prepare_notifications(
        self,
        next_event_before: Optional[Event],
        changed_events: List[Event],
    ) -> List[UserNotification]:
        """Proceed upcoming subscriptions"""
        # Prepare notifications list and timestamp
        notifications: List[UserNotification] = []
        timestamp = datetime.now(tz=timezone(get_config().bot.timezone))

        # Get current and next event
        current_event = await self.uow.events.get_current_event()
        if not current_event:
            return notifications
        next_event = await self.uow.events.get_next_event()

        # Preparing global notifications
        if next_event != next_event_before:
            await self._throttle_global_announcement()
            text = await global_announcement_template.render_async(
                {"current_event": current_event, "next_event": next_event},
            )
            for user in await self.uow.users.get_receive_all_announcements_users():
                notifications.append(
                    UserNotification(
                        user_id=user.id,
                        text=text,
                        bottom_text="(управление уведомлениями - /notifications)",
                        timestamp=timestamp,
                    ),
                )

        # Checking subscriptions
        for subscription in await self.uow.subscriptions.get_upcoming_subscriptions():
            notify = False
            for e in changed_events:
                if current_event.position <= e.position <= subscription.event.position:
                    notify = True
            if notify:
                await self.uow.session.refresh(subscription.event, ["real_position"])
                text = await subscription_template.render_async(
                    {
                        "current_event": current_event,
                        "subscription": subscription,
                    },
                )
                notifications.append(
                    UserNotification(
                        user_id=subscription.user_id,
                        text=text,
                        bottom_text="(управление уведомлениями - /notifications)",
                        timestamp=timestamp,
                    ),
                )
            if subscription.event is current_event:
                await self.uow.session.delete(subscription)

        return notifications

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def skip_event(self, event_id: int) -> Tuple[EventDTO, DeliveryInfo]:
        """Mark event as skipped
        @param event_id:
        @return: Skipped event
        """
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound(event_id)

        current_event = await self.uow.events.get_current_event()
        if event is current_event:
            raise CurrentEventNotAllowed
        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            event.skip = not event.skip
            await self.uow.session.flush([event])
            await self.uow.session.refresh(event, ["real_position"])
            notifications = await self._prepare_notifications(
                next_event_before=next_event,
                changed_events=[event],
            )
            await self.uow.commit()
            delivery_info = await NotificationService(
                self.uow, self.identity
            ).send_notifications(notifications)
            logger.info(
                f"Event id={event.id} was skipped by user id={self.identity.id}\n"
                f"Delivery: {delivery_info}"
            )
            return event.to_dto(), delivery_info

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def swap_events(
        self,
        event1_id: int,
        event2_id: int,
    ) -> Tuple[EventDTO, EventDTO, DeliveryInfo]:
        """Swap two schedule positions
        @param event1_id:
        @param event2_id:
        @return: Tuple of both schedule
        """
        if event1_id == event2_id:
            raise SameEventsAreNotAllowed
        event1 = await self.uow.events.get_event(event1_id)
        if not event1:
            raise EventNotFound(event1_id)
        event2 = await self.uow.events.get_event(event2_id)
        if not event2:
            raise EventNotFound(event2_id)

        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            event1.position, event2.position = event2.position, event1.position
            await self.uow.session.flush([event1, event2])
            await self.uow.session.refresh(event1, ["real_position"])
            await self.uow.session.refresh(event2, ["real_position"])
            notifications = await self._prepare_notifications(
                next_event_before=next_event,
                changed_events=[event1, event2],
            )
            await self.uow.commit()
            delivery_info = await NotificationService(
                self.uow, self.identity
            ).send_notifications(notifications)
            logger.info(
                f"Event id={event1.id} was swapped with Event id={event2.id} "
                f"by User id={self.identity.id}\n"
                f"Delivery: {delivery_info}"
            )
            return event1.to_dto(), event2.to_dto(), delivery_info

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_current_event(self, event_id: int) -> Tuple[EventDTO, DeliveryInfo]:
        """Set event as current
        @param event_id:
        @return: Current event
        """
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound
        if event.skip:
            raise SkippedEventNotAllowed

        current_event = await self.uow.events.get_current_event()
        if current_event:
            if event is current_event:
                raise CurrentEventNotAllowed
            current_event.current = None
            await self.uow.session.flush([current_event])
        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            event.current = True
            await self.uow.session.flush([event])
            notifications = await self._prepare_notifications(
                next_event_before=next_event,
                changed_events=[event],
            )
            await self.uow.commit()
            delivery_info = await NotificationService(
                self.uow, self.identity
            ).send_notifications(notifications)
            logger.info(
                f"Event id={event.id} was set as current by User id={self.identity.id}"
            )
            return event.to_dto(), delivery_info

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_next_event(self) -> Tuple[EventDTO, DeliveryInfo]:
        """Sets next event as current
        @return: Current event
        """
        current_event = await self.uow.events.get_current_event()
        if current_event:
            next_event = await self.uow.events.get_next_event()
            if not next_event:
                raise NoNextEvent
        else:
            next_event = await self.uow.events.get_event_by_real_position(1)
            if not next_event:
                raise EventNotFound
        return await self.set_current_event(next_event.id)
