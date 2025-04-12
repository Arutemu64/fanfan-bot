from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram_dialog import BgManagerFactory, ShowMode
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream import Logger
from faststream.nats import NatsRouter, PullSub
from nats.js import JetStreamContext

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.core.events.notifications import CancelMailingEvent
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "notification.mailing.cancel",
    stream=stream,
    pull_sub=PullSub(),
    durable="notification_mailing_cancel",
)
@inject
async def cancel_mailing(
    data: CancelMailingEvent,
    mailing_repo: FromDishka[MailingRepository],
    bot: FromDishka[Bot],
    bgm_factory: FromDishka[BgManagerFactory],
    js: FromDishka[JetStreamContext],
    logger: Logger,
) -> None:
    subject = f"mailing.{data.mailing_id}"
    await js.purge_stream("stream", subject=subject)
    while message := await mailing_repo.pop_message(data.mailing_id):
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id,
            )
            # Update current dialog (in case if it's information is now outdated)
            bg = bgm_factory.bg(
                bot=bot, user_id=message.chat.id, chat_id=message.chat.id, load=True
            )
            await bg.update(data={}, show_mode=ShowMode.EDIT)
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
        else:
            logger.info(
                "Deleted message %s for user %s from mailing %s",
                message.message_id,
                message.chat.id,
                data.mailing_id,
                extra={"deleted_message": message.model_dump_json(exclude_none=True)},
            )
    await mailing_repo.set_as_cancelled(data.mailing_id)
    logger.info("Mailing %s was cancelled", data.mailing_id)
    return
