import logging
import uuid
from typing import List, Optional

from aiogram.types import Message
from redis.asyncio import Redis
from taskiq import TaskiqResult
from taskiq_redis.exceptions import ResultIsMissingError

from fanfan.application.dto.notification import DeliveryInfo, UserNotification
from fanfan.application.services.base import BaseService
from fanfan.config import get_config
from fanfan.infrastructure.scheduler import (
    redis_async_result,
)
from fanfan.infrastructure.scheduler.tasks import delete_message, send_notification

logger = logging.getLogger(__name__)


class NotificationService(BaseService):
    async def send_notifications(
        self,
        notifications: List[UserNotification],
        delivery_id: Optional[str] = None,
    ) -> DeliveryInfo:
        """Send a list of notifications to users
        @param notifications: List of UserNotification
        @param delivery_id:
        """
        if delivery_id is None:
            delivery_id = uuid.uuid4().hex
        logger.info(f"Delivery id={delivery_id} started by user id={self.identity.id}")
        for n in notifications:
            await send_notification.kiq(notification=n, delivery_id=delivery_id)
        return DeliveryInfo(delivery_id=delivery_id, count=len(notifications))

    async def delete_delivery(self, delivery_id: str) -> DeliveryInfo:
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
        logger.info(
            f"Delivery id={delivery_id} ({count}) "
            f"was deleted by user id={self.identity.id}"
        )
        return DeliveryInfo(delivery_id=delivery_id, count=count)
