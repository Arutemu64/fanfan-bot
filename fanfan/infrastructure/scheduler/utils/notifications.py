import logging
import uuid
from itertools import groupby
from typing import List, Optional

from aiogram.types import Message
from dishka import make_async_container
from redis.asyncio import Redis

from fanfan.application.dto.notification import DeliveryInfo, UserNotification
from fanfan.infrastructure.di.config import ConfigProvider
from fanfan.infrastructure.di.redis import RedisProvider
from fanfan.infrastructure.scheduler.tasks import (
    delete_message,
    send_notification,
)

logger = logging.getLogger(__name__)


async def send_notifications(
    notifications: List[UserNotification],
    delivery_id: Optional[str] = None,
) -> DeliveryInfo:
    """Send a list of notifications to users
    @param notifications: List of UserNotification
    @param delivery_id:
    """
    if delivery_id is None:
        delivery_id = uuid.uuid4().hex
    logger.info(f"Delivery id={delivery_id} started")
    for user_id, user_notifications in groupby(notifications, lambda n: n.user_id):
        await send_notification.kiq(
            user_id=user_id,
            user_notifications=user_notifications,
            delivery_id=delivery_id,
        )
    return DeliveryInfo(delivery_id=delivery_id, count=len(notifications))


async def delete_delivery(delivery_id: str) -> DeliveryInfo:
    """Mass delete sent notifications by group ID
    @param delivery_id: Delivery ID
    """
    container = make_async_container(ConfigProvider(), RedisProvider())
    async with container() as container:
        redis = await container.get(Redis)
        key = f"delivery:{delivery_id}"
        count = await redis.llen(key)
        while await redis.llen(key) > 0:
            await delete_message.kiq(
                message=Message.model_validate(await redis.lpop(key))
            )
        logger.info(f"Delivery id={delivery_id} ({count}) " f"was deleted")
    await container.close()
    return DeliveryInfo(delivery_id=delivery_id, count=count)
