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
subscription_template = jinja.from_string(
    "{% if current_event.id == subscription.event_id %}"
        "Выступление {{ subscription.event.participant.title or subscription.event.title }} "
        "<b>НАЧАЛОСЬ!</b>"
    "{% else %}"
        "До выступления {{ subscription.event.participant.title or subscription.event.title }} "
        "осталось <b>{{ counter }} выступлений</b>"
    "{% endif %}"
)

global_announcement_template = jinja.from_string(
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

        if send_global_announcement:
            next_event = await db.event.get_one(
                and_(Event.position > current_event.position, Event.hidden != True),
                order_by=Event.position,
            )
            announcement = global_announcement_template.render(
                {"current_event": current_event, "next_event": next_event}
            )
            receive_all_users = await db.user.get_many(
                User.receive_all_announcements == True
            )  # noqa
            for user in receive_all_users:
                await send_personal_notification(bot, user.id, announcement)

        subscriptions = await db.subscription.get_many(
            and_(
                Subscription.counter >= (Subscription.event_id - current_event.id),
                (Subscription.event_id - current_event.id) >= 0,
                # Subscription.user.has(User.receive_all_announcements == False),  # noqa
                Subscription.event.has(Event.hidden != True),
            ),
        )
        for subscription in subscriptions:
            counter = await db.event.get_count(
                and_(
                    Event.position >= current_event.position,
                    Event.position < subscription.event.position,
                    Event.hidden != True,
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
            if current_event.id - subscription.event_id == 0:
                await db.session.delete(subscription)
                await db.session.commit()
