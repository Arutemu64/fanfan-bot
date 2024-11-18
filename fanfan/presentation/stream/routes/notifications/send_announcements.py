import enum
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from faststream.nats import NatsBroker, NatsRouter, PullSub
from jinja2 import Environment
from pydantic import BaseModel
from pytz import timezone

from fanfan.adapters.config.models import Configuration
from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.core.dto.mailing import MailingId
from fanfan.core.dto.notification import UserNotification
from fanfan.core.models.event import EventModel
from fanfan.presentation.stream.jstream import stream
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)
from fanfan.presentation.tgbot.keyboards.buttons import (
    OPEN_SUBSCRIPTIONS_BUTTON,
    PULL_DOWN_DIALOG,
)

router = NatsRouter()


class EventChangeType(enum.StrEnum):
    SET_AS_CURRENT = "set_as_current"
    MOVE = "move"
    SKIP = "skip"
    UNSKIP = "unskip"


class EventChangeDTO(BaseModel):
    event: EventModel
    type: EventChangeType


class SendAnnouncementsDTO(BaseModel):
    send_global_announcement: bool
    event_changes: list[EventChangeDTO]
    mailing_id: MailingId


@router.subscriber(
    "send_announcements",
    stream=stream,
    pull_sub=PullSub(),
    durable="send_announcements",
)
async def prepare_announcements(  # noqa: C901
    data: SendAnnouncementsDTO,
    events: FromDishka[EventsRepository],
    users: FromDishka[UsersRepository],
    subscriptions: FromDishka[SubscriptionsRepository],
    mailing: FromDishka[MailingRepository],
    config: FromDishka[Configuration],
    jinja: FromDishka[Environment],
    broker: FromDishka[NatsBroker],
) -> None:
    time = datetime.now(tz=timezone(config.timezone)).strftime("%H:%M")
    counter = 0

    # Prepare templates
    global_announcement_template = jinja.get_template(
        "global_announcement.jinja2",
    )
    subscription_template = jinja.get_template(
        "subscription_notification.jinja2",
    )

    # Get current and next event
    current_event = await events.get_current_event()
    if not current_event:
        return

    # Send global announcement
    if data.send_global_announcement:
        next_event = await events.get_next_event()
        text = await global_announcement_template.render_async(
            {
                "current_event": current_event,
                "next_event": next_event,
            },
        )
        notification = UserNotification(
            title=f"📢 НА СЦЕНЕ ({time})",
            text=text,
            reply_markup=InlineKeyboardBuilder(
                [[OPEN_SUBSCRIPTIONS_BUTTON], [PULL_DOWN_DIALOG]],
            ).as_markup(),
        )
        for u in await users.get_users_by_receive_all_announcements():
            await broker.publish(
                SendNotificationDTO(user_id=u.id, notification=notification),
                subject=f"mailing.{data.mailing_id}",
                stream="stream",
            )
            counter += 1

    # Checking subscriptions
    for subscription in await subscriptions.get_upcoming_subscriptions():
        reason: str | None = None
        notify = False
        for e in data.event_changes:
            if current_event.order <= e.event.order <= subscription.event.order:
                notify = True
                match e.type:
                    case EventChangeType.MOVE:
                        reason = f"(Выступление №{e.event.id} было перемещено)"
                    case EventChangeType.SKIP:
                        reason = f"(Выступление №{e.event.id} было пропущено)"
                    case EventChangeType.UNSKIP:
                        reason = f"(Выступление №{e.event.id} вернулось)"
        if notify:
            text = await subscription_template.render_async(
                {
                    "event": subscription.event,
                    "current_event": current_event,
                },
            )
            await broker.publish(
                SendNotificationDTO(
                    user_id=subscription.user_id,
                    notification=UserNotification(
                        title=f"📢 СКОРО НА СЦЕНЕ ({time})",
                        text=text,
                        bottom_text=reason,
                        reply_markup=InlineKeyboardBuilder(
                            [[OPEN_SUBSCRIPTIONS_BUTTON], [PULL_DOWN_DIALOG]],
                        ).as_markup(),
                    ),
                ),
                subject=f"mailing.{data.mailing_id}",
                stream="stream",
            )
            counter += 1
    await mailing.update_total(data.mailing_id, counter)
    return
