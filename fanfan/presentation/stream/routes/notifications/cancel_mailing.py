from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream import Logger
from faststream.nats import NatsRouter, PullSub
from nats.js import JetStreamContext

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.core.models.mailing import MailingId
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "cancel_mailing",
    stream=stream,
    pull_sub=PullSub(),
    durable="cancel_mailing",
)
@inject
async def cancel_mailing(
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
                extra={"deleted_message": message.model_dump_json(exclude_none=True)},
            )
    await mailing_repo.set_as_cancelled(mailing_id)
    logger.info("Mailing %s was cancelled", mailing_id)
    return
