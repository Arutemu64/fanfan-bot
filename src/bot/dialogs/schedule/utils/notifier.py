import logging

import jinja2
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import and_, select

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
        "Выступление {{ subscription.event.joined_title }} "
        "<b>НАЧАЛОСЬ!</b>"
    "{% else %}"
        "{% set counter = subscription.event.real_position - current_event.real_position %}"  # noqa: E501
        "До выступления {{ subscription.event.joined_title }} "
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
        "<b>Сейчас:</b> {{ current_event.joined_title }}\n"
    "{% endif %}"
    "{% if next_event %}"
        "<b>Затем:</b> {{ next_event.joined_title }}\n"
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
            user_ids = (
                await db.session.execute(
                    select(User.id).where(User.receive_all_announcements.is_(True))
                )
            ).all()
            for user_id in list(zip(*user_ids))[0]:
                await send_personal_notification(bot, user_id, announcement_text)

        subscriptions = await db.subscription.get_many(
            Subscription.event.has(
                and_(
                    Event.skip.isnot(True),
                    Subscription.counter
                    >= (Event.real_position - current_event.real_position),
                    (Event.real_position - current_event.real_position) >= 0,
                ),
            ),
        )
        for subscription in subscriptions:
            text = subscription_template.render(
                {
                    "current_event": current_event,
                    "subscription": subscription,
                }
            )
            await send_personal_notification(bot, subscription.user_id, text)
            if current_event is subscription.event:
                await db.session.delete(subscription)
        await db.session.commit()
