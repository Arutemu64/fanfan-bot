import enum
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.nats import NatsRouter, PullSub
from jinja2 import Environment
from pydantic import BaseModel
from pytz import timezone

from fanfan.adapters.config.models import Configuration
from fanfan.adapters.db.repositories.events import EventsRepository
from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.core.dto.notification import UserNotification
from fanfan.core.models.event import Event
from fanfan.core.models.mailing import MailingId
from fanfan.presentation.stream.jstream import stream
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)
from fanfan.presentation.tgbot.keyboards.buttons import (
    OPEN_SUBSCRIPTIONS_BUTTON,
    PULL_DOWN_DIALOG,
)

ANNOUNCEMENT_REPLY_MARKUP = InlineKeyboardBuilder(
    [[OPEN_SUBSCRIPTIONS_BUTTON], [PULL_DOWN_DIALOG]],
).as_markup()

router = NatsRouter()


class EventChangeType(enum.StrEnum):
    SET_AS_CURRENT = enum.auto()
    MOVE = enum.auto()
    SKIP = enum.auto()
    UNSKIP = enum.auto()


class EventChangeDTO(BaseModel):
    event: Event
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
@inject
async def send_announcements(  # noqa: C901
    data: SendAnnouncementsDTO,
    events_repo: FromDishka[EventsRepository],
    users_repo: FromDishka[UsersRepository],
    subscriptions_repo: FromDishka[SubscriptionsRepository],
    mailing_repo: FromDishka[MailingRepository],
    config: FromDishka[Configuration],
    jinja: FromDishka[Environment],
    broker_adapter: FromDishka[StreamBrokerAdapter],
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
    current_event = await events_repo.get_current_event()
    if not current_event:
        return

    # Send global announcement
    if data.send_global_announcement:
        next_event = await events_repo.get_next_event()
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
            await broker_adapter.send_notification(
                SendNotificationDTO(user_id=u.id, notification=notification),
                mailing_id=data.mailing_id,
            )
            counter += 1

    # Checking subscriptions
    for subscription in await subscriptions_repo.get_upcoming_subscriptions(
        queue=current_event.queue
    ):
        reason: str | None = None
        notify = False
        for e in data.event_changes:
            if current_event.order <= e.event.order <= subscription.event.order:
                notify = True
                match e.type:
                    case EventChangeType.MOVE:
                        reason = f"(Выступление №{e.event.id} было перемещено 🔀)"
                    case EventChangeType.SKIP:
                        reason = f"(Выступление №{e.event.id} было снято 🚫)"
                    case EventChangeType.UNSKIP:
                        reason = f"(Выступление №{e.event.id} вернулось 🙉)"
        if notify:
            text = await subscription_template.render_async(
                {
                    "event": subscription.event,
                    "current_event": current_event,
                },
            )
            await broker_adapter.send_notification(
                SendNotificationDTO(
                    user_id=subscription.user_id,
                    notification=UserNotification(
                        title=f"🔔 УВЕДОМЛЕНИЕ О ПОДПИСКЕ ({time})",
                        text=text,
                        bottom_text=reason,
                        reply_markup=ANNOUNCEMENT_REPLY_MARKUP,
                    ),
                ),
                mailing_id=data.mailing_id,
            )
            counter += 1
    await mailing_repo.update_total(data.mailing_id, counter)
    return
