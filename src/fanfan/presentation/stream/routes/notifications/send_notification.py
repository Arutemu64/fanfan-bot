from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram_dialog import BgManagerFactory, ShowMode
from dishka import FromDishka
from dishka_faststream import inject
from faststream import AckPolicy, Logger
from faststream.nats import NatsMessage, NatsRouter, PullSub

from fanfan.adapters.bot.notifier import TelegramNotifier
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.core.events.notifications import NewNotificationEvent
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "notifications.new",
    stream=stream,
    pull_sub=PullSub(),
    durable="notifications_new",
    ack_policy=AckPolicy.MANUAL,
)
@inject
async def send_notification(
    data: NewNotificationEvent,
    msg: FromDishka[NatsMessage],
    notifier: FromDishka[TelegramNotifier],
    bot: FromDishka[Bot],
    bgm_factory: FromDishka[BgManagerFactory],
    mailing_repo: FromDishka[MailingDAO],
    users_repo: FromDishka[UsersRepository],
    logger: Logger,
) -> None:
    # Check if mailing is active
    if data.mailing_id:
        mailing_data = await mailing_repo.get_mailing_data(data.mailing_id)
        if mailing_data.is_cancelled:
            await msg.reject()
            return

    # Check if user is reachable
    user = await users_repo.get_user_by_id(data.user_id)
    if user.tg_id is None:
        await msg.reject()
        return

    try:
        # Send message
        message = await notifier.send_notification(
            tg_id=user.tg_id,
            notification=data.notification,
        )
        # Update current dialog (in case if it's information is now outdated)
        bg = bgm_factory.bg(bot=bot, user_id=user.tg_id, chat_id=user.tg_id, load=True)
        await bg.update(data={}, show_mode=ShowMode.EDIT)
    except TelegramRetryAfter as e:
        await msg.nack(delay=e.retry_after)
        logger.warning(
            "Retrying sending a message to %s in %s", data.user_id, e.retry_after
        )
        return
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        await msg.reject()
        if data.mailing_id:
            await mailing_repo.add_processed(data.mailing_id, None)
        logger.info("Skipping sending message to %s", data.user_id, exc_info=e)
        return
    else:
        await msg.ack()
        if data.mailing_id:
            await mailing_repo.add_processed(
                mailing_id=data.mailing_id, message=message
            )
        logger.info(
            "Sent message %s to user %s via mailing %s",
            message.message_id,
            data.user_id,
            data.mailing_id,
            extra={
                "sent_message": message.model_dump_json(exclude_none=True),
                "mailing_id": data.mailing_id,
            },
        )
    return
