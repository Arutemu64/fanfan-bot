import logging

import jinja2
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import and_

from src.bot.ui import strings
from src.db import Database
from src.db.database import create_session_maker
from src.db.models import Event, Subscription, User

session_pool = create_session_maker()

DELETE_BUTTON = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text=strings.buttons.viewed, callback_data="delete")
)

jinja = jinja2.Environment()

# fmt: off
subscription_template = jinja.from_string(  # noqa: E501
    "{% if current_event.id == subscription.event_id %}"
        "Выступление {{ subscription.event.participant.title or subscription.event.title }} "  # noqa: E501
        "<b>НАЧАЛОСЬ!</b>"
    "{% else %}"
        "До выступления {{ subscription.event.participant.title or subscription.event.title }} "  # noqa: E501
        "осталось "
        "{% if (counter % 10 == 1) and (counter % 100 != 11) %}"
            "<b>{{ counter }} выступление</b>"
        "{% elif (2 <= counter % 10 <= 4) and (counter % 100 < 10 or counter % 100 >= 20) %}"  # noqa: E501
            "<b>{{ counter }} выступления</b>"
        "{% else %}"
            "<b>{{ counter }} выступлений</b>"
        "{% endif %}"
    "{% endif %}"
)

global_announcement_template = jinja.from_string(  # noqa: E501
    "{% if current_event %}"
        "<b>Сейчас:</b> {{ current_event.participant.title or current_event.title }}\n"
    "{% endif %}"
    "{% if next_event %}"
        "<b>Затем:</b> {{ next_event.participant.title or next_event.title }}\n"
    "{% endif %}"
)
# fmt: on


async def send_personal_notification(bot: Bot, user_id: int, text: str):
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"<b>📢 ПЕРСОНАЛЬНОЕ УВЕДОМЛЕНИЕ</b>\n{text}",
            reply_markup=DELETE_BUTTON.as_markup(),
        )
    except TelegramBadRequest:
        logging.info(f"Can't send notification to user {user_id}, skipping...")


async def proceed_subscriptions(
    bot: Bot,
    send_global_announcement: bool = False,
):
    async with session_pool() as session:
        db = Database(session)

        current_event = await db.event.get_current()
        if not current_event:
            return

        if send_global_announcement:
            next_event = await db.event.get_next(current_event)
            announcement_text = global_announcement_template.render(
                {"current_event": current_event, "next_event": next_event}
            )
            receive_all_users = await db.user.get_many(
                User.receive_all_announcements.is_(True)
            )  # noqa
            for user in receive_all_users:
                await send_personal_notification(bot, user.id, announcement_text)

        subscriptions = await db.subscription.get_many(
            and_(
                Subscription.event.has(Event.hidden.isnot(True)),
                Subscription.event.has(
                    Subscription.counter >= (Event.position - current_event.position)
                ),
            ),
        )
        for subscription in subscriptions:
            counter = await db.event.get_count(
                and_(
                    Event.position >= current_event.position,
                    Event.position < subscription.event.position,
                    Event.hidden.isnot(True),
                )
            )
            text = subscription_template.render(
                {
                    "current_event": current_event,
                    "subscription": subscription,
                    "counter": counter,
                }
            )
            await send_personal_notification(bot, subscription.user_id, text)
            if current_event is subscription.event:
                await db.session.delete(subscription)
                await db.session.commit()
