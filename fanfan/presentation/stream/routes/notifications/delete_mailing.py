from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from dishka import FromDishka
from faststream import Logger
from faststream.nats import NatsRouter, PullSub
from nats.js import JetStreamContext

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.core.dto.mailing import MailingId
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "delete_mailing",
    stream=stream,
    pull_sub=PullSub(),
    durable="delete_mailing",
)
async def delete_mailing(
    mailing_id: MailingId,
    mailing_repo: FromDishka[MailingRepository],
    bot: FromDishka[Bot],
    js: FromDishka[JetStreamContext],
    logger: Logger,
) -> None:
    subject = f"mailing.{mailing_id}"
    await js.purge_stream("stream", subject=subject)
    while message := await mailing_repo.pop_message(mailing_id):
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id,
            )
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
        else:
            logger.info(
                "Deleted message %s for user %s from mailing %s",
                message.message_id,
                message.chat.id,
                mailing_id,
            )
    logger.info("Mailing %s was deleted", mailing_id)
    return
