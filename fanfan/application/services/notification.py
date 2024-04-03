from datetime import datetime
from typing import List, Optional

from aiogram.types import Message
from jinja2 import Environment, FileSystemLoader
from pytz import timezone
from redis.asyncio import Redis
from taskiq import TaskiqResult
from taskiq_redis.exceptions import ResultIsMissingError

from fanfan.application.dto.common import UserNotification
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole
from fanfan.config import get_config
from fanfan.infrastructure.scheduler import (
    delete_message,
    redis_async_result,
    send_notification,
)
from fanfan.presentation.tgbot import JINJA_TEMPLATES_DIR

templateLoader = FileSystemLoader(searchpath=JINJA_TEMPLATES_DIR)
jinja = Environment(
    lstrip_blocks=True, trim_blocks=True, loader=templateLoader, enable_async=True
)
subscription_template = jinja.get_template("subscription_notification.jinja2")
global_announcement_template = jinja.get_template("global_announcement.jinja2")


class NotificationService(BaseService):
    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def send_notifications(
        self, notifications: List[UserNotification], delivery_id: Optional[str] = None
    ) -> None:
        """
        Send a list of notifications to users
        @param notifications: List of UserNotification
        @param delivery_id:
        """
        for n in notifications:
            await send_notification.kiq(notification=n, delivery_id=delivery_id)

    @check_permission(allowed_roles=[UserRole.ORG])
    async def delete_delivery(self, delivery_id: str) -> int:
        """
        Mass delete sent notifications by group ID
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
                        Message.model_validate(result.return_value)
                    )
                    await redis.delete(task_id)
            except ResultIsMissingError:
                pass
        await redis.aclose()
        return count

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def proceed_subscriptions(
        self, send_global_announcement: bool = False
    ) -> None:
        """
        Proceed upcoming subscriptions and send notifications
        @param send_global_announcement: If True,
        all users with receive_all_announcements enabled
        will receive a global Now/Next notification
        @return:
        """
        current_event = await self.uow.events.get_current_event()
        if not current_event:
            return

        notifications = []
        timestamp = datetime.now(tz=timezone(get_config().bot.timezone))

        if send_global_announcement:
            next_event = await self.uow.events.get_next_event(event_id=current_event.id)
            text = await global_announcement_template.render_async(
                {"current_event": current_event, "next_event": next_event}
            )
            for user in await self.uow.users.get_receive_all_announcements_users():
                notifications.append(
                    UserNotification(user_id=user.id, text=text, timestamp=timestamp)
                )

        for subscription in await self.uow.subscriptions.get_upcoming_subscriptions():
            text = await subscription_template.render_async(
                {
                    "current_event": current_event,
                    "subscription": subscription,
                }
            )
            notifications.append(
                UserNotification(
                    user_id=subscription.user_id, text=text, timestamp=timestamp
                )
            )

        await self.send_notifications(notifications)

        async with self.uow:
            await self.uow.subscriptions.bulk_delete_subscriptions_by_event(
                current_event.id
            )
            await self.uow.commit()
