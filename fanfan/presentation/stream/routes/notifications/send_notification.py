from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram_dialog import BgManagerFactory, ShowMode
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream import Logger, Path
from faststream.nats import NatsMessage, NatsRouter, PullSub

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.core.events.notifications import NewNotificationEvent
from fanfan.core.models.mailing import MailingId
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "notifications.new",
    stream=stream,
    pull_sub=PullSub(),
    durable="notifications_new",
)
@router.subscriber(
    "notifications.mailing.{mailing_id}",
    stream=stream,
    pull_sub=PullSub(),
    durable="notifications_mailing",
)
@inject
async def send_notification(
    data: NewNotificationEvent,
    msg: FromDishka[NatsMessage],
    notifier: FromDishka[BotNotifier],
    bot: FromDishka[Bot],
    bgm_factory: FromDishka[BgManagerFactory],
    mailing_repo: FromDishka[MailingRepository],
    logger: Logger,
    mailing_id: MailingId | None = Path(default=None),  # noqa: B008
) -> None:
    try:
        # Send message
        message = await notifier.send_notification(
            user_id=data.user_id,
            notification=data.notification,
        )
        # Update current dialog (in case if it's information is now outdated)
        bg = bgm_factory.bg(
            bot=bot, user_id=data.user_id, chat_id=data.user_id, load=True
        )
        await bg.update(data={}, show_mode=ShowMode.EDIT)
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
