from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter, TextInput
from aiogram_dialog.widgets.text import Const
from sqlalchemy import and_

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import get_events_query_terms
from src.db import Database
from src.db.models import Event, Subscription

SUBSCRIBE_EVENT_ID_INPUT = "subscribe_event_id_input"


async def check_subscription(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    terms = get_events_query_terms(
        False, dialog_manager.dialog_data.get("search_query")
    )
    event = await db.event.get_by_where(and_(Event.id == data, *terms))

    if not event:
        text = "⚠️ Выступление не найдено!"
        if dialog_manager.dialog_data.get("search_query"):
            text += "\n(убедитесь, что оно входит в результаты поиска)"
        await message.reply(text)
        return
    if event.hidden:
        await message.reply("⚠️ Нельзя подписаться на скрытое выступление!")
        return
    subscription = await db.subscription.get_by_where(
        and_(
            Subscription.event_id == event.id,
            Subscription.user_id == message.from_user.id,
        )
    )
    if subscription:
        await db.session.delete(subscription)
        await db.session.commit()
        await message.reply("🗑️ Подписка удалена!")
        await dialog_manager.switch_to(states.SCHEDULE.MAIN)
    else:
        await dialog_manager.switch_to(states.SCHEDULE.ASK_SUBSCRIPTION_COUNTER)


async def setup_subscription(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    event_count = await db.event.get_count()
    if event_count < data < 1:
        await message.reply("⚠️ Некорректное значение")
        return

    event_id = dialog_manager.find(SUBSCRIBE_EVENT_ID_INPUT).get_value()
    counter = data

    subscription = await db.subscription.new(
        event_id=event_id, user_id=message.from_user.id, counter=counter
    )
    db.session.add(subscription)
    await db.session.commit()
    await db.session.refresh(subscription)
    await message.reply(
        f"✅ Подписка на выступление <b>{subscription.event.title or subscription.event.participant.title}</b>"
        f" успешно оформлена!"
    )
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


setup_subscription_window = Window(
    Const("🔢 За сколько выступлений до выбранного начать оповещать Вас?"),
    TextInput(id="counter_input", type_factory=int, on_success=setup_subscription),
    state=states.SCHEDULE.ASK_SUBSCRIPTION_COUNTER,
)
