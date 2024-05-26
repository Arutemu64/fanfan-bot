import logging
import time
from datetime import datetime
from typing import List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader
from pytz import timezone

from fanfan.application.dto.event import EventDTO, UpdateEventDTO
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
from fanfan.common.enums import UserRole
from fanfan.config import get_config
from fanfan.infrastructure.scheduler.utils.notifications import send_notifications
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
        announcement_timestamp = await self.uow.settings.get_announcement_timestamp()
        timestamp = time.time()
        if (timestamp - announcement_timestamp) < settings.announcement_timeout:
            raise AnnounceTooFast(
                settings.announcement_timeout,
                int(
                    announcement_timestamp + settings.announcement_timeout - timestamp,
                ),
            )
        else:
            await self.uow.settings.update_announcement_timestamp(timestamp=timestamp)

    async def _prepare_notifications(
        self,
        next_event_before: Optional[EventDTO],
        changed_events: List[EventDTO],
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
            print(current_event)
            print(subscription.event)
            for e in changed_events:
                if current_event.order <= e.order <= subscription.event.order:
                    notify = True
            if notify:
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

        await self.uow.subscriptions.bulk_delete_subscriptions(current_event.id)

        return notifications

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def skip_event(self, event_id: int) -> Tuple[EventDTO, DeliveryInfo]:
        """Mark event as skipped
        @param event_id:
        @return: Skipped event
        """
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound(event_id=event_id)

        current_event = await self.uow.events.get_current_event()
        if event is current_event:
            raise CurrentEventNotAllowed
        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            await self.uow.events.update_event(
                UpdateEventDTO(
                    id=event.id,
                    skip=not event.skip,
                ),
            )
            await self.uow.flush()
            event = await self.uow.events.get_event(event_id)
            notifications = await self._prepare_notifications(
                next_event_before=next_event,
                changed_events=[event],
            )
            await self.uow.commit()
            delivery_info = await send_notifications(notifications)
            logger.info(
                f"Event id={event.id} was skipped by user id={self.identity.id}\n"
                f"Delivery: {delivery_info}"
            )
            return event, delivery_info

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def move_event(
        self, event_id: int, after_event_id: int
    ) -> Tuple[EventDTO, EventDTO, DeliveryInfo]:
        """
        Move selected event after another event
        @param event_id: Selected event
        @param after_event_id: Event to place after
        @return:
        """
        if event_id == after_event_id:
            raise SameEventsAreNotAllowed
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound(event_id=event_id)
        after_event = await self.uow.events.get_event(after_event_id)
        if not after_event:
            raise EventNotFound(event_id=after_event_id)
        next_event = await self.uow.events.get_next_event()
        before_event = await self.uow.events.get_next_by_order(after_event.id)
        async with self.uow:
            await self.uow.events.update_event(
                UpdateEventDTO(
                    id=event_id,
                    order=(after_event.order + before_event.order) / 2
                    if before_event
                    else after_event.order + 0.5,
                ),
            )
            await self.uow.flush()
            event = await self.uow.events.get_event(event_id)
            notifications = await self._prepare_notifications(
                next_event_before=next_event, changed_events=[event]
            )
            await self.uow.commit()
            delivery_info = await send_notifications(notifications)
            logger.info(
                f"Event id={event.id} was placed after event id={after_event_id} "
                f"by User id={self.identity.id}\n"
                f"Delivery: {delivery_info}"
            )
            return event, after_event, delivery_info

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_current_event(self, event_id: int) -> Tuple[EventDTO, DeliveryInfo]:
        """Set event as current
        @param event_id:
        @return: Current event
        """
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound(event_id=event_id)
        if event.skip:
            raise SkippedEventNotAllowed

        current_event = await self.uow.events.get_current_event()
        if current_event:
            if event is current_event:
                raise CurrentEventNotAllowed
            await self.uow.events.update_event(
                UpdateEventDTO(
                    id=current_event.id,
                    current=None,
                ),
            )
            await self.uow.flush()
        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            await self.uow.events.update_event(
                UpdateEventDTO(
                    id=event_id,
                    current=True,
                ),
            )
            await self.uow.flush()
            notifications = await self._prepare_notifications(
                next_event_before=next_event,
                changed_events=[event],
            )
            await self.uow.commit()
            delivery_info = await send_notifications(notifications)
            logger.info(
                f"Event id={event.id} was set as current by User id={self.identity.id}"
            )
            return event, delivery_info

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_next_event(self) -> Tuple[EventDTO, DeliveryInfo]:
        """Sets next event as current
        @return: Current event
        """
        next_event = await self.uow.events.get_next_event()
        if not next_event:
            raise NoNextEvent
        return await self.set_current_event(next_event.id)
