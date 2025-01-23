from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import Message
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream import Logger
from faststream.nats import NatsMessage, NatsRouter, PullSub
from pydantic import BaseModel

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.core.dto.notification import UserNotification
from fanfan.core.models.mailing import MailingId
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


class EditNotificationDTO(BaseModel):
    message: Message
    notification: UserNotification
    mailing_id: MailingId | None


@router.subscriber(
    "edit_notification",
    stream=stream,
    pull_sub=PullSub(),
    durable="edit_notification",
)
@inject
async def edit_notification(
    data: EditNotificationDTO,
    mailing_repo: FromDishka[MailingRepository],
    msg: FromDishka[NatsMessage],
    notifier: FromDishka[BotNotifier],
    logger: Logger,
) -> None:
    try:
        new_message = await notifier.edit_notification(
            message=data.message, notification=data.notification
        )
        if data.mailing_id:
            await mailing_repo.add_processed(
                mailing_id=data.mailing_id, message=new_message
            )
    except TelegramRetryAfter as e:
        await msg.nack(delay=e.retry_after)
        logger.warning(
            "Retrying editing message %s for user %s in %s",
            data.message.message_id,
            data.message.chat.id,
            e.retry_after,
        )
        return
    except (TelegramBadRequest, TelegramForbiddenError):
        await msg.reject()
        logger.warning(
            "Skipping editing message %s for user %s",
            data.message.message_id,
            data.message.chat.id,
            exc_info=True,
        )
        return
    else:
        await msg.ack()
        logger.info(
            "Edited notification message %s for user %s",
            data.message.message_id,
            data.message.chat.id,
            extra={"notification": data.notification},
        )
