from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from dishka import FromDishka
from faststream import Path
from faststream.nats import NatsMessage, NatsRouter, PullSub
from pydantic import BaseModel

from fanfan.core.models.mailing import MailingId
from fanfan.core.models.notification import UserNotification
from fanfan.core.models.user import UserId
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository
from fanfan.infrastructure.stream.stream import stream

router = NatsRouter()


class SendNotificationDTO(BaseModel):
    user_id: UserId
    notification: UserNotification


@router.subscriber(
    "send_notification", stream=stream, pull_sub=PullSub(), max_workers=3
)
@router.subscriber(
    "mailing.{mailing_id}", stream=stream, pull_sub=PullSub(), max_workers=3
)
async def send_notification(
    data: SendNotificationDTO,
    msg: FromDishka[NatsMessage],
    bot: FromDishka[Bot],
    mailing_manager: FromDishka[MailingRepository],
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
        await msg.ack()
    except TelegramRetryAfter as e:
        await msg.nack(delay=e.retry_after)
        return
    except (TelegramBadRequest, TelegramForbiddenError):
        await msg.reject()
        return
    if mailing_id:
        await mailing_manager.add_to_sent(
            mailing_id=mailing_id,
            message=message,
        )
