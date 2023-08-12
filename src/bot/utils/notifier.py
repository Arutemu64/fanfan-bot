import logging

import jinja2
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import and_

from src.db import Database
from src.db.database import create_session_maker
from src.db.models import Event, Subscription

session_pool = create_session_maker()

jinja = jinja2.Environment()

# fmt: off
template = jinja.from_string(
    "<b>📢 ПЕРСОНАЛЬНОЕ УВЕДОМЛЕНИЕ</b>\n"
    "{% if current_event.id - subscription.event_id == 0 %}"
        "{% if subscription.event.participant %}"
            "Выступление {{ subscription.event.participant.title }}"
        "{% else %}"
            "Событие {{ subscription.event.title }}"
        "{% endif %}"
        " НАЧАЛОСЬ!"
    "{% else %}"
        "{% if subscription.event.participant %}"
            "До выступления {{ subscription.event.participant.title }}"
        "{% else %}"
            "До события {{ subscription.event.title }}"
        "{% endif %}"
        " осталось {{ subscription.event_id - current_event.id }} выступлений"
    "{% endif %}"
)
# fmt: on


async def send_subscription_notifications(
    bot: Bot,
):
    async with session_pool() as session:
        db = Database(session)
        current_event = await db.event.get_by_where(Event.current == True)  # noqa
        subscriptions = await db.subscription.get_many(
            and_(
                Subscription.counter >= (Subscription.event_id - current_event.id),
                (Subscription.event_id - current_event.id) >= 0,
            ),
            limit=1000,
        )
        for subscription in subscriptions:
            text = template.render(
                {"current_event": current_event, "subscription": subscription}
            )
            try:
                await bot.send_message(chat_id=subscription.user_id, text=text)
            except TelegramBadRequest:
                logging.info(
                    f"Can't send notification to user {subscription.user_id}, skipping..."
                )
            if current_event.id - subscription.event_id == 0:
                await db.session.delete(subscription)
                await db.session.commit()
