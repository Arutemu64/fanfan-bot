import contextlib

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from dishka import FromDishka
from faststream.nats import NatsRouter, PullSub
from nats.js import JetStreamContext

from fanfan.core.models.mailing import MailingId
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository
from fanfan.infrastructure.stream.stream import stream

router = NatsRouter()


@router.subscriber("delete_mailing", stream=stream, pull_sub=PullSub())
async def delete_mailing(
    mailing_id: MailingId,
    manager: FromDishka[MailingRepository],
    bot: FromDishka[Bot],
    js: FromDishka[JetStreamContext],
) -> None:
    subject = f"mailing.{mailing_id}"
    await js.purge_stream("stream", subject=subject)
    while message := await manager.pop_message(mailing_id):
        with contextlib.suppress(TelegramBadRequest, TelegramForbiddenError):
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id,
            )
