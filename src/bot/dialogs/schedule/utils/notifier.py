import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from jinja2 import Environment, FileSystemLoader

from src.bot import TEMPLATES_DIR
from src.bot.dialogs.common import DELETE_BUTTON
from src.db import Database
from src.db.database import create_session_maker

session_pool = create_session_maker()
jinja = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR), lstrip_blocks=True, trim_blocks=True
)

subscription_template = jinja.get_template("subscription_announcement.jinja2")
global_announcement_template = jinja.get_template("global_announcement.jinja2")


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
            for user_id in await db.user.get_receive_all_announcements_user_ids():
                await send_personal_notification(bot, user_id, announcement_text)

        subscriptions = await db.subscription.get_all_upcoming(current_event)
        for_delete = []
        for subscription in subscriptions:
            text = subscription_template.render(
                {
                    "current_event": current_event,
                    "subscription": subscription,
                }
            )
            await send_personal_notification(bot, subscription.user_id, text)
            if current_event is subscription.event:
                for_delete.append(subscription.id)
        await db.subscription.batch_delete(for_delete)
        await db.session.commit()
