from aiogram import Bot
from sqlalchemy import and_

from src.db import Database
from src.db.models import Event, Subscription


async def send_subscription_notifications(
    bot: Bot,
    db: Database,
):
    current_event = await db.event.get_by_where(Event.current == True)  # noqa
    subscriptions = await db.subscription.get_many(
        and_(
            Subscription.counter >= (Subscription.event_id - current_event.id),
            (Subscription.event_id - current_event.id) >= 0,
        ),
        limit=1000,
    )
    for subscription in subscriptions:
        if current_event.id - subscription.event_id == 0:
            text = (
                f"<b>📢 ПЕРСОНАЛЬНОЕ УВЕДОМЛЕНИЕ</b>\n"
                f"Выступление {subscription.event.participant.title} НАЧАЛОСЬ!"
            )
        else:
            text = (
                f"<b>📢 ПЕРСОНАЛЬНОЕ УВЕДОМЛЕНИЕ</b>\n"
                f"До выступления {subscription.event.participant.title} осталось {subscription.event_id - current_event.id} выступлений"
            )
        await bot.send_message(chat_id=subscription.user_id, text=text)
        if current_event.id - subscription.event_id == 0:
            await db.session.delete(subscription)
            await db.session.commit()
    return
