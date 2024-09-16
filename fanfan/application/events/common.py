from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from jinja2 import Environment, FileSystemLoader
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.common.config import get_config
from fanfan.core.models.notification import UserNotification
from fanfan.infrastructure.db.models import Event, Subscription, User, UserSettings
from fanfan.infrastructure.db.queries.events import next_event_query
from fanfan.infrastructure.db.queries.subscriptions import upcoming_subscriptions_query
from fanfan.presentation.tgbot import JINJA_TEMPLATES_DIR
from fanfan.presentation.tgbot.keyboards.buttons import (
    OPEN_SUBSCRIPTIONS_BUTTON,
    PULL_DOWN_DIALOG,
)

ANNOUNCEMENT_TIMESTAMP = "announcement_timestamp"
ANNOUNCEMENT_LOCK = "announcement_lock"


async def prepare_notifications(
    session: AsyncSession,
    next_event_before: Event | None,
    changed_events: list[Event | None],
) -> list[UserNotification]:
    # Prepare
    config = get_config()
    time = datetime.now(tz=timezone(config.timezone)).strftime("%H:%M")
    notifications: list[UserNotification] = []

    # Setup Jinja
    jinja = Environment(
        lstrip_blocks=True,
        trim_blocks=True,
        loader=FileSystemLoader(searchpath=JINJA_TEMPLATES_DIR),
        enable_async=True,
        autoescape=True,
    )
    subscription_template = jinja.get_template(
        "subscription_notification.jinja2",
    )
    global_announcement_template = jinja.get_template(
        "global_announcement.jinja2",
    )

    # Get current and next event
    current_event = await session.scalar(select(Event).where(Event.current.is_(True)))
    if not current_event:
        return notifications
    next_event = await session.scalar(next_event_query())

    # Preparing global notifications
    if next_event != next_event_before:
        text = await global_announcement_template.render_async(
            {
                "current_event": current_event,
                "next_event": next_event,
            },
        )
        users = await session.scalars(
            select(User).where(
                User.settings.has(UserSettings.receive_all_announcements.is_(True))
            )
        )
        notifications += [
            UserNotification(
                user_id=u.id,
                title=f"📢 НА СЦЕНЕ ({time})",
                text=text,
                reply_markup=InlineKeyboardBuilder(
                    [[OPEN_SUBSCRIPTIONS_BUTTON], [PULL_DOWN_DIALOG]],
                ).as_markup(),
            )
            for u in users
        ]

    # Checking subscriptions
    subscriptions = await session.scalars(
        upcoming_subscriptions_query().options(
            joinedload(Subscription.event).undefer(Event.queue)
        )
    )
    for subscription in subscriptions:
        notify = False
        for e in changed_events:
            if current_event.order <= e.order <= subscription.event.order:
                notify = True
        if notify:
            text = await subscription_template.render_async(
                {
                    "current": subscription.event is current_event,
                    "id": subscription.event.id,
                    "title": subscription.event.title,
                    "counter": subscription.event.queue - current_event.queue,
                },
            )
            notifications.append(
                UserNotification(
                    user_id=subscription.user_id,
                    title=f"📢 СКОРО НА СЦЕНЕ ({time})",
                    text=text,
                    reply_markup=InlineKeyboardBuilder(
                        [[OPEN_SUBSCRIPTIONS_BUTTON], [PULL_DOWN_DIALOG]],
                    ).as_markup(),
                ),
            )

    return notifications
