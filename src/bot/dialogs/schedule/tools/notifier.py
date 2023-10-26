from arq import ArqRedis
from jinja2 import Environment
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.dialogs.templates import global_announcement, subscription_notification
from src.bot.structures import Notification
from src.config import conf
from src.db import Database
from src.db.database import create_async_engine

jinja = Environment(lstrip_blocks=True, trim_blocks=True)
subscription_template = jinja.from_string(subscription_notification)
global_announcement_template = jinja.from_string(global_announcement)


async def proceed_subscriptions(
    arq: ArqRedis,
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
            await arq.enqueue_job("send_notification", Notification(user.id, text))

    subscriptions = await db.subscription.get_all_upcoming(current_event)
    for sub in subscriptions:
        text = subscription_template.render(
            {
                "current_event": current_event,
                "subscription": sub,
            }
        )
        await arq.enqueue_job("send_notification", Notification(sub.user_id, text))
        if sub.event is current_event:
            await session.delete(sub)
    await session.commit()
    await session.close()
    await engine.dispose()
