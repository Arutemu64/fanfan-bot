from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from dishka import FromDishka
from faststream import Logger, Path
from faststream.nats import NatsMessage, NatsRouter, PullSub

from fanfan.core.models.mailing import MailingId
from fanfan.core.models.notification import SendNotificationDTO
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository
from fanfan.presentation.faststream.stream import stream

router = NatsRouter()


@router.subscriber(
    "send_notification",
    stream=stream,
    pull_sub=PullSub(),
    durable="send_notification",
    max_workers=3,
    retry=True,
)
@router.subscriber(
    "mailing.{mailing_id}",
    stream=stream,
    pull_sub=PullSub(),
    durable="mailings",
    max_workers=3,
    retry=True,
)
async def send_notification(
    data: SendNotificationDTO,
    msg: FromDishka[NatsMessage],
    bot: FromDishka[Bot],
    mailing_manager: FromDishka[MailingRepository],
    logger: Logger,
    mailing_id: MailingId | None = Path(default=None),  # noqa: B008
) -> None:
    try:
        if data.notification.image_id:
            message = await bot.send_photo(
                chat_id=data.user_id,
                photo=str(data.notification.image_id),
                caption=data.notification.render_message_text(),
                reply_markup=data.notification.reply_markup,
            )
        else:
            message = await bot.send_message(
                chat_id=data.user_id,
                text=data.notification.render_message_text(),
                reply_markup=data.notification.reply_markup,
            )
    except TelegramRetryAfter as e:
        await msg.nack(delay=e.retry_after)
        logger.warning(
            "Retrying sending a message to %s in %s", data.user_id, e.retry_after
        )
        return
    except (TelegramBadRequest, TelegramForbiddenError):
        await msg.reject()
        logger.info("Skipping sending message to %s", data.user_id)
        return
    else:
        await msg.ack()
        logger.info(
            "Sent message %s to user %s",
            message.message_id,
            data.user_id,
            extra={"sent_message": message, "mailing_id": mailing_id},
        )
    if mailing_id:
        await mailing_manager.add_to_sent(
            mailing_id=mailing_id,
            message=message,
        )
    return
