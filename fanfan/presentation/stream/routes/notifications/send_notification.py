from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from dishka import FromDishka
from faststream import Logger, Path
from faststream.nats import NatsMessage, NatsRouter, PullSub
from pydantic import BaseModel

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.core.dto.notification import UserNotification
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.user import UserId
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


class SendNotificationDTO(BaseModel):
    user_id: UserId
    notification: UserNotification


@router.subscriber(
    "send_notification",
    stream=stream,
    pull_sub=PullSub(),
    durable="send_notification",
    retry=True,
)
@router.subscriber(
    "mailing.{mailing_id}",
    stream=stream,
    pull_sub=PullSub(),
    durable="mailings",
    retry=True,
)
async def send_notification(
    data: SendNotificationDTO,
    msg: FromDishka[NatsMessage],
    notifier: FromDishka[BotNotifier],
    mailing_repo: FromDishka[MailingRepository],
    logger: Logger,
    mailing_id: MailingId | None = Path(default=None),  # noqa: B008
) -> None:
    try:
        message = await notifier.send_notification(
            user_id=data.user_id,
            notification=data.notification,
        )
    except TelegramRetryAfter as e:
        await msg.nack(delay=e.retry_after)
        logger.warning(
            "Retrying sending a message to %s in %s", data.user_id, e.retry_after
        )
        return
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        await msg.reject()
        if mailing_id:
            await mailing_repo.add_processed(mailing_id, None)
        logger.info("Skipping sending message to %s", data.user_id, exc_info=e)
        return
    else:
        await msg.ack()
        if mailing_id:
            await mailing_repo.add_processed(mailing_id=mailing_id, message=message)
        logger.info(
            "Sent message %s to user %s via mailing %s",
            message.message_id,
            data.user_id,
            mailing_id,
            extra={
                "sent_message": message.model_dump_json(exclude_none=True),
                "mailing_id": mailing_id,
            },
        )
    return
