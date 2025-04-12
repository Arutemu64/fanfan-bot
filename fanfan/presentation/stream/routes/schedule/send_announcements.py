from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.nats import NatsRouter, PullSub
from jinja2 import Environment
from pytz import timezone

from fanfan.adapters.config.models import Configuration
from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.core.dto.notification import UserNotification
from fanfan.core.events.notifications import NewNotificationEvent
from fanfan.core.events.schedule import ScheduleChangedEvent
from fanfan.core.exceptions.schedule import ScheduleChangeNotFound
from fanfan.core.models.schedule_change import (
    ScheduleChangeFull,
    ScheduleChangeType,
)
from fanfan.presentation.stream.jstream import stream
from fanfan.presentation.tgbot.keyboards.buttons import (
    OPEN_SUBSCRIPTIONS_BUTTON,
    PULL_DOWN_DIALOG,
    undo_schedule_change_button,
)

ANNOUNCEMENT_REPLY_MARKUP = InlineKeyboardBuilder(
    [[OPEN_SUBSCRIPTIONS_BUTTON], [PULL_DOWN_DIALOG]],
).as_markup()

router = NatsRouter()


def resolve_change_reason(schedule_change: ScheduleChangeFull) -> str | None:
    if schedule_change.type is ScheduleChangeType.SET_AS_CURRENT:
        if schedule_change.changed_event:
            return f"🔥 Выступление №{schedule_change.changed_event.id} началось"
        return f"🚫 С выступления №{schedule_change.argument_event.id} снята отметка"
    if schedule_change.type is ScheduleChangeType.MOVED:
        return f"🔀 Выступление №{schedule_change.changed_event.id} перенесено"
    if schedule_change.type is ScheduleChangeType.SKIPPED:
        return f"🚫 Выступление №{schedule_change.changed_event.id} было снято"
    if schedule_change.type is ScheduleChangeType.UNSKIPPED:
        return f"🙉 Выступление №{schedule_change.changed_event.id} вернулось"
    return None


@router.subscriber(
    "schedule.changed",
    stream=stream,
    pull_sub=PullSub(),
    durable="schedule_changed",
)
@inject
async def send_announcements(  # noqa: C901
    data: ScheduleChangedEvent,
    schedule_repo: FromDishka[ScheduleRepository],
    users_repo: FromDishka[UsersRepository],
    subscriptions_repo: FromDishka[SubscriptionsRepository],
    uow: FromDishka[UnitOfWork],
    mailing_repo: FromDishka[MailingRepository],
    config: FromDishka[Configuration],
    jinja: FromDishka[Environment],
    events_broker: FromDishka[EventsBroker],
) -> None:
    time = datetime.now(tz=timezone(config.timezone)).strftime("%H:%M")
    counter = 0

    # Get schedule change
    schedule_change = await schedule_repo.get_schedule_change(
        schedule_change_id=data.schedule_change_id
    )
    if schedule_change is None:
        raise ScheduleChangeNotFound

    # Prepare templates
    global_announcement_template = jinja.get_template(
        "global_announcement.jinja2",
    )
    subscription_template = jinja.get_template(
        "subscription_notification.jinja2",
    )

    # Create and save mailing ID
    if schedule_change.mailing_id:
        mailing_id = schedule_change.mailing_id
    else:
        mailing_id = await mailing_repo.create_new_mailing(
            by_user_id=schedule_change.user_id
        )
        async with uow:
            schedule_change.mailing_id = mailing_id
            await schedule_repo.save_schedule_change(schedule_change)
            await uow.commit()

    # Notify schedule editors first
    editors_notification = UserNotification(
        title="✏️ ИЗМЕНЕНИЕ РАСПИСАНИЯ",
        text=f"@{schedule_change.user.username} сделал изменение в расписании:\n"
        f"{resolve_change_reason(schedule_change)}",
        reply_markup=InlineKeyboardBuilder(
            [
                [undo_schedule_change_button(schedule_change_id=schedule_change.id)],
                [PULL_DOWN_DIALOG],
            ]
        ).as_markup(),
    )
    for editor in await users_repo.get_schedule_editors():
        await events_broker.publish(
            NewNotificationEvent(
                user_id=editor.id,
                notification=editors_notification,
                mailing_id=mailing_id,
            )
        )

    # Get current and next event
    current_event = await schedule_repo.get_current_event()
    if not current_event:
        return
    next_event = await schedule_repo.get_next_event()

    # Send global announcement
    if schedule_change.send_global_announcement:
        text = await global_announcement_template.render_async(
            {
                "current_event": current_event,
                "next_event": next_event,
            },
        )
        notification = UserNotification(
            title=f"📣 НА СЦЕНЕ ({time})",
            text=text,
            reply_markup=ANNOUNCEMENT_REPLY_MARKUP,
        )
        for u in await users_repo.get_users_by_receive_all_announcements():
            await events_broker.publish(
                NewNotificationEvent(
                    user_id=u.id, notification=notification, mailing_id=mailing_id
                )
            )
            counter += 1

    # Checking subscriptions
    for subscription in await subscriptions_repo.get_upcoming_subscriptions(
        queue=current_event.queue
    ):
        if (
            current_event.order
            <= schedule_change.changed_event.order
            <= subscription.event.order
        ):
            text = await subscription_template.render_async(
                {
                    "event": subscription.event,
                    "current_event": current_event,
                },
            )
            await events_broker.publish(
                NewNotificationEvent(
                    user_id=subscription.user_id,
                    notification=UserNotification(
                        title=f"🔔 УВЕДОМЛЕНИЕ О ПОДПИСКЕ ({time})",
                        text=text,
                        bottom_text=resolve_change_reason(schedule_change),
                        reply_markup=ANNOUNCEMENT_REPLY_MARKUP,
                    ),
                    mailing_id=mailing_id,
                )
            )
            counter += 1
    await mailing_repo.update_total(mailing_id, counter)
    return
