import asyncio
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
from fanfan.adapters.nats.events_broker import EventsBroker
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.core.dto.notification import UserNotification
from fanfan.core.dto.schedule import ScheduleEventDTO
from fanfan.core.events.notifications import NewNotificationEvent
from fanfan.core.events.schedule import NewScheduleChange
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeType,
)
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
    schedule_change: ScheduleChange,
    changed_event: ScheduleEventDTO | None,
    argument_event: ScheduleEventDTO | None,
) -> str | None:
    match schedule_change.type:
        case ScheduleChangeType.SET_AS_CURRENT:
            if changed_event:
                return f"🔥 Выступление №{changed_event.public_id:03d} началось"
            if argument_event:
                return (
                    f"⛔ Выступление №{argument_event.public_id:03d} больше не текущее"
                )
        case ScheduleChangeType.MOVED:
            return f"🔀 Выступление №{changed_event.public_id:03d} перенесено"
        case ScheduleChangeType.SKIPPED:
            return f"🚫 Выступление №{changed_event.public_id:03d} было снято"
        case ScheduleChangeType.UNSKIPPED:
            return f"🙉 Выступление №{changed_event.public_id:03d} вернулось"
    return None


@router.subscriber(
    "schedule.change.new",
    stream=stream,
    pull_sub=PullSub(),
    durable="schedule_change_new",
)
@inject
async def proceed_schedule_change(
    data: NewScheduleChange,
    schedule_repo: FromDishka[ScheduleEventsRepository],
    changes_repo: FromDishka[ScheduleChangesRepository],
    users_repo: FromDishka[UsersRepository],
    subscriptions_repo: FromDishka[SubscriptionsRepository],
    mailing_repo: FromDishka[MailingDAO],
    config: FromDishka[EnvConfig],
    jinja: FromDishka[StreamJinjaEnvironment],
    events_broker: FromDishka[EventsBroker],
) -> None:
    now = datetime.now(tz=timezone(config.timezone)).strftime("%H:%M")

    global_announcement_template = jinja.get_template(
        "global_announcement.jinja2",
    )
    subscription_template = jinja.get_template(
        "subscription_notification.jinja2",
    )

    schedule_change = await changes_repo.get_schedule_change(data.schedule_change_id)

    changed_event = (
        await schedule_repo.read_event_by_id(schedule_change.changed_event_id)
        if schedule_change.changed_event_id
        else None
    )
    argument_event = (
        await schedule_repo.read_event_by_id(schedule_change.argument_event_id)
        if schedule_change.argument_event_id
        else None
    )

    reason_msg = get_schedule_change_reason_msg(
        schedule_change=schedule_change,
        changed_event=changed_event,
        argument_event=argument_event,
    )

    notification_events: list[NewNotificationEvent] = []

    # Notify editors
    editor = await users_repo.get_user_by_id(schedule_change.user_id)
    editors_notification = UserNotification(
        title="✏️ ИЗМЕНЕНИЕ РАСПИСАНИЯ",
        text=f"@{editor.username} сделал изменение в расписании:\n{reason_msg}",
        reply_markup=InlineKeyboardBuilder(
            [
                [undo_schedule_change_button(schedule_change_id=schedule_change.id)],
                [PULL_DOWN_DIALOG],
            ]
        ).as_markup(),
    )
    notification_events.extend(
        NewNotificationEvent(
            user_id=e.id,
            notification=editors_notification,
            mailing_id=schedule_change.mailing_id,
        )
        for e in await users_repo.read_schedule_editors()
    )

    current_event = await schedule_repo.read_current_event()
    next_event = await schedule_repo.read_next_event() if current_event else None

    # Global announcement
    if schedule_change.send_global_announcement and current_event:
        text = await global_announcement_template.render_async(
            {
                "current_event": current_event,
                "next_event": next_event,
            }
        )
        notification = UserNotification(
            title=f"📣 НА СЦЕНЕ ({now})",
            text=text,
            reply_markup=ANNOUNCEMENT_REPLY_MARKUP,
        )
        notification_events.extend(
            NewNotificationEvent(
                user_id=u.id,
                notification=notification,
                mailing_id=schedule_change.mailing_id,
            )
            for u in await users_repo.read_all_by_receive_all_announcements()
        )

    # Subscriptions
    if current_event and changed_event:
        upcoming_subscriptions = await subscriptions_repo.read_upcoming_subscriptions(
            current_event_queue=current_event.queue
        )
        for s in upcoming_subscriptions:
            # Compare by order, queue might be None
            if current_event.order <= changed_event.order <= s.event.order:
                text = await subscription_template.render_async(
                    {
                        "event_public_id": s.event.public_id,
                        "event_title": s.event.title,
                        "queue_difference": s.event.queue - current_event.queue,
                        "time_diff": s.event.cumulative_duration
                        - current_event.cumulative_duration,
                        "reason_msg": reason_msg,
                    }
                )
                notification_events.append(
                    NewNotificationEvent(
                        user_id=s.user_id,
                        notification=UserNotification(
                            title=f"🔔 УВЕДОМЛЕНИЕ О ПОДПИСКЕ ({now})",
                            text=text,
                            reply_markup=ANNOUNCEMENT_REPLY_MARKUP,
                        ),
                        mailing_id=schedule_change.mailing_id,
                    )
                )

    await mailing_repo.update_total(
        mailing_id=schedule_change.mailing_id,
        total_count=len(notification_events),
    )

    await asyncio.gather(*(events_broker.publish(e) for e in notification_events))
