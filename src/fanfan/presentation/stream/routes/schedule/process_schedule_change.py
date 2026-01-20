from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from dishka_faststream import inject
from faststream.nats import NatsRouter, PullSub
from pytz import timezone

from fanfan.adapters.config.models import EnvConfig
from fanfan.adapters.db.repositories.schedule_changes import ScheduleChangesRepository
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.nats.events_broker import EventsBroker
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.core.dto.notification import UserNotification
from fanfan.core.events.notifications import NewNotificationEvent
from fanfan.core.events.schedule import ScheduleChanged
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeType,
)
from fanfan.core.models.schedule_event import ScheduleEvent
from fanfan.presentation.stream.jinja.factory import StreamJinjaEnvironment
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


def get_schedule_change_reason_msg(
    schedule_change: ScheduleChange, changed_event: ScheduleEvent
) -> str | None:
    if schedule_change.type is ScheduleChangeType.SET_AS_CURRENT:
        return f"🔥 Выступление №{changed_event.public_id} началось"
    if schedule_change.type is ScheduleChangeType.MOVED:
        return f"🔀 Выступление №{changed_event.public_id} перенесено"
    if schedule_change.type is ScheduleChangeType.SKIPPED:
        return f"🚫 Выступление №{changed_event.public_id} было снято"
    if schedule_change.type is ScheduleChangeType.UNSKIPPED:
        return f"🙉 Выступление №{changed_event.public_id} вернулось"
    return None


@router.subscriber(
    "schedule.change.new",
    stream=stream,
    pull_sub=PullSub(),
    durable="schedule_change_new",
)
@inject
async def proceed_schedule_change(
    data: ScheduleChanged,
    schedule_repo: FromDishka[ScheduleEventsRepository],
    changes_repo: FromDishka[ScheduleChangesRepository],
    users_repo: FromDishka[UsersRepository],
    subscriptions_repo: FromDishka[SubscriptionsRepository],
    uow: FromDishka[UnitOfWork],
    mailing_repo: FromDishka[MailingDAO],
    config: FromDishka[EnvConfig],
    jinja: FromDishka[StreamJinjaEnvironment],
    events_broker: FromDishka[EventsBroker],
) -> None:
    # Prepare timers
    time = datetime.now(tz=timezone(config.timezone)).strftime("%H:%M")
    counter = 0

    # Prepare templates
    global_announcement_template = jinja.get_template(
        "global_announcement.jinja2",
    )
    subscription_template = jinja.get_template(
        "subscription_notification.jinja2",
    )

    # Save schedule change into DB
    async with uow:
        change = ScheduleChange(
            type=data.type,
            changed_event_id=data.changed_event_id,
            argument_event_id=data.argument_event_id,
            mailing_id=data.mailing_id,
            user_id=data.user_id,
            send_global_announcement=data.send_global_announcement,
        )
        change = await changes_repo.add_schedule_change(change)
        await uow.commit()

    changed_event = await schedule_repo.get_event_by_id(data.changed_event_id)
    reason_msg = get_schedule_change_reason_msg(change, changed_event)

    # Notify schedule editors first
    editor = await users_repo.get_user_by_id(change.user_id)
    editors_notification = UserNotification(
        title="✏️ ИЗМЕНЕНИЕ РАСПИСАНИЯ",
        text=f"@{editor.username} сделал изменение в расписании:\n{reason_msg}",
        reply_markup=InlineKeyboardBuilder(
            [
                [undo_schedule_change_button(schedule_change_id=change.id)],
                [PULL_DOWN_DIALOG],
            ]
        ).as_markup(),
    )
    for e in await users_repo.read_schedule_editors():
        await events_broker.publish(
            NewNotificationEvent(
                user_id=e.id,
                notification=editors_notification,
                mailing_id=change.mailing_id,
            )
        )

    # Get current and next event
    current_event = await schedule_repo.read_current_event()
    if not current_event:
        return
    next_event = await schedule_repo.read_next_event()

    # Send global announcement
    if change.send_global_announcement:
        text = await global_announcement_template.render_async(
            {
                "current_event": current_event,
                "next_event": next_event,
            }
        )
        notification = UserNotification(
            title=f"📣 НА СЦЕНЕ ({time})",
            text=text,
            reply_markup=ANNOUNCEMENT_REPLY_MARKUP,
        )
        for u in await users_repo.read_all_by_receive_all_announcements():
            await events_broker.publish(
                NewNotificationEvent(
                    user_id=u.id,
                    notification=notification,
                    mailing_id=change.mailing_id,
                )
            )
            counter += 1

    # Checking subscriptions
    changed_event = await schedule_repo.read_event_by_id(change.changed_event_id)
    for s in await subscriptions_repo.read_upcoming_subscriptions(current_event.queue):
        if current_event.order <= changed_event.order <= s.event.order:
            text = await subscription_template.render_async(
                {
                    "event_public_id": s.event.public_id,
                    "event_title": s.event.title,
                    "queue_difference": s.event.queue - current_event.queue,
                    "time_diff": s.event.cumulative_duration
                    - current_event.cumulative_duration,
                    "reason_msg": reason_msg,
                },
            )
            await events_broker.publish(
                NewNotificationEvent(
                    user_id=s.user_id,
                    notification=UserNotification(
                        title=f"🔔 УВЕДОМЛЕНИЕ О ПОДПИСКЕ ({time})",
                        text=text,
                        reply_markup=ANNOUNCEMENT_REPLY_MARKUP,
                    ),
                    mailing_id=change.mailing_id,
                )
            )
            counter += 1
    await mailing_repo.update_total(change.mailing_id, counter)
    return
