import time
from datetime import datetime
from typing import List, Optional

from aiogram.types import Message
from jinja2 import Environment, FileSystemLoader
from pytz import timezone
from redis.asyncio import Redis
from taskiq import TaskiqResult
from taskiq_redis.exceptions import ResultIsMissingError

from fanfan.application.dto.common import UserNotification
from fanfan.application.exceptions.event import AnnounceTooFast
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole
from fanfan.config import get_config
from fanfan.infrastructure.db.models import Event
from fanfan.infrastructure.scheduler import (
    delete_message,
    redis_async_result,
    send_notification,
)
from fanfan.presentation.tgbot import JINJA_TEMPLATES_DIR

templateLoader = FileSystemLoader(searchpath=JINJA_TEMPLATES_DIR)
jinja = Environment(
    lstrip_blocks=True,
    trim_blocks=True,
    loader=templateLoader,
    enable_async=True,
)
subscription_template = jinja.get_template("subscription_notification.jinja2")
global_announcement_template = jinja.get_template("global_announcement.jinja2")


class NotificationService(BaseService):
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

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def send_notifications(
        self,
        notifications: List[UserNotification],
        delivery_id: Optional[str] = None,
    ) -> None:
        """Send a list of notifications to users
        @param notifications: List of UserNotification
        @param delivery_id:
        """
        for n in notifications:
            await send_notification.kiq(notification=n, delivery_id=delivery_id)

    @check_permission(allowed_roles=[UserRole.ORG])
    async def delete_delivery(self, delivery_id: str) -> int:
        """Mass delete sent notifications by group ID
        @param delivery_id: Delivery ID
        """
        redis = Redis().from_url(get_config().redis.build_connection_str())
        count = await redis.llen(delivery_id)
        while await redis.llen(delivery_id) > 0:
            try:
                task_id = await redis.lpop(delivery_id)
                result: TaskiqResult = await redis_async_result.get_result(task_id)
                if not result.is_err:
                    await delete_message.kiq(
                        Message.model_validate(result.return_value),
                    )
                    await redis.delete(task_id)
            except ResultIsMissingError:
                pass
        await redis.aclose()
        return count

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def proceed_subscriptions(
        self,
        current_event_before: Optional[Event],
        next_event_before: Optional[Event],
        changed_events: List[Event],
    ) -> None:
        """Proceed upcoming subscriptions and send notifications"""
        # Prepare notifications list and timestamp
        notifications = []
        timestamp = datetime.now(tz=timezone(get_config().bot.timezone))

        # Get current and next event
        current_event = await self.uow.events.get_current_event()
        if not current_event:
            return
        next_event = await self.uow.events.get_next_event()

        # Preparing global notifications
        if (current_event != current_event_before) or (next_event != next_event_before):
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
                        timestamp=timestamp,
                    ),
                )
            if subscription.event is current_event:
                await self.uow.session.delete(subscription)

        async with self.uow:
            await self.uow.commit()
            await self.send_notifications(notifications)
