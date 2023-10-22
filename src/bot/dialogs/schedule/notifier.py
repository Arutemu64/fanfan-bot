from aiogram import Bot
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot import TEMPLATES_DIR
from src.bot.utils.notifications import Notification, queue
from src.config import conf
from src.db import Database
from src.db.database import create_async_engine

jinja = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR), lstrip_blocks=True, trim_blocks=True
)
subscription_template = jinja.get_template("subscription_announcement.jinja2")
global_announcement_template = jinja.get_template("global_announcement.jinja2")


async def proceed_subscriptions(
    bot: Bot,
    send_global_announcement: bool = False,
):
    engine = create_async_engine(conf.db.build_connection_str())
    session = AsyncSession(bind=engine)
    db = Database(session)

    current_event = await db.event.get_current()
    if not current_event:
        return

    if send_global_announcement:
        next_event = await db.event.get_next(current_event)
        text = global_announcement_template.render(
            {"current_event": current_event, "next_event": next_event}
        )
        for user in await db.user.get_receive_all_announcements_users():
            await queue.put(Notification(user.id, text))

    subscriptions = await db.subscription.get_all_upcoming(current_event)
    for sub in subscriptions:
        text = subscription_template.render(
            {
                "current_event": current_event,
                "subscription": sub,
            }
        )
        await queue.put(Notification(sub.user.id, text))
        if sub.event is current_event:
            await session.delete(sub)
    await session.commit()
    await session.close()
    await engine.dispose()
