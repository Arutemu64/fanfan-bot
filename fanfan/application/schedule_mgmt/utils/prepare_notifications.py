import enum
from dataclasses import dataclass
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from jinja2 import Environment
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.common.config import Configuration
from fanfan.core.models.notification import UserNotification
from fanfan.infrastructure.db.models import Event, Subscription, User, UserSettings
from fanfan.infrastructure.db.queries.events import next_event_query
from fanfan.infrastructure.db.queries.subscriptions import upcoming_subscriptions_query
from fanfan.presentation.tgbot.keyboards.buttons import (
    OPEN_SUBSCRIPTIONS_BUTTON,
    PULL_DOWN_DIALOG,
)


class EventChangeType(enum.StrEnum):
    SET_AS_CURRENT = "set_as_current"
    MOVE = "move"
    SKIP = "skip"
    UNSKIP = "unskip"


@dataclass
class EventChangeDTO:
    event: Event
    type: EventChangeType


class PrepareNotifications:
    def __init__(
        self, session: AsyncSession, config: Configuration, jinja: Environment
    ):
        self.session = session
        self.config = config
        self.jinja = jinja

    async def __call__(
        self,
        session: AsyncSession,
        next_event_before: Event | None,
        event_changes: list[EventChangeDTO | None],
    ) -> list[UserNotification]:
        # Prepare
        time = datetime.now(tz=timezone(self.config.timezone)).strftime("%H:%M")
        notifications: list[UserNotification] = []

        # Prepare templates
        subscription_template = self.jinja.get_template(
            "subscription_notification.jinja2",
        )
        global_announcement_template = self.jinja.get_template(
            "global_announcement.jinja2",
        )

        # Get current and next event
        current_event = await session.scalar(
            select(Event)
            .where(Event.current.is_(True))
            .options(joinedload(Event.block))
        )
        if not current_event:
            return notifications
        next_event = await session.scalar(
            next_event_query().options(joinedload(Event.block))
        )

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
                joinedload(Subscription.event).joinedload(Event.block)
            )
        )
        for subscription in subscriptions:
            reason: str | None = None
            notify = False
            for e in event_changes:
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
                notifications.append(
                    UserNotification(
                        user_id=subscription.user_id,
                        title=f"📢 СКОРО НА СЦЕНЕ ({time})",
                        text=text,
                        bottom_text=reason,
                        reply_markup=InlineKeyboardBuilder(
                            [[OPEN_SUBSCRIPTIONS_BUTTON], [PULL_DOWN_DIALOG]],
                        ).as_markup(),
                    ),
                )

        return notifications
