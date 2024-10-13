import enum
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from faststream.nats import NatsBroker, NatsRouter, PullSub
from jinja2 import Environment
from pydantic import BaseModel
from pytz import timezone

from fanfan.core.models.event import EventModel
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.notification import UserNotification
from fanfan.infrastructure.config_reader import Configuration
from fanfan.infrastructure.db.repositories.events import EventsRepository
from fanfan.infrastructure.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.infrastructure.db.repositories.users import UsersRepository
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository
from fanfan.infrastructure.stream.routes.send_notification import (
    SendNotificationDTO,
)
from fanfan.infrastructure.stream.stream import stream
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


class PrepareAnnouncementsDTO(BaseModel):
    send_global_announcement: bool
    event_changes: list[EventChangeDTO | None]
    mailing_id: MailingId


@router.subscriber("prepare_announcements", stream=stream, pull_sub=PullSub())
async def prepare_announcements(
    data: PrepareAnnouncementsDTO,
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
