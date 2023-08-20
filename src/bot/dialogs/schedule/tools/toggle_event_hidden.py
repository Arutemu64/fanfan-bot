import asyncio

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const
from sqlalchemy import and_

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    EventsList,
    SchedulePaginator,
    get_events_query_terms,
    get_schedule,
    on_wrong_event_id,
    set_current_schedule_page,
)
from src.bot.ui import strings
from src.bot.utils import notifier
from src.db import Database
from src.db.models import Event


async def toggle_event_hidden(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    # Получаем выступление (с учётом поиска), проверяем его существование
    terms = get_events_query_terms(True, dialog_manager.dialog_data.get("search_query"))
    event = await db.event.get_by_where(and_(Event.id == data, *terms))
    if not event:
        text = "⚠️ Выступление не найдено!"
        if dialog_manager.dialog_data.get("search_query"):
            text += "\n(убедитесь, что оно входит в результаты поиска)"
        await message.reply(text)
        return

    # Проверяем, что выступление не отмечено как текущее
    if event.current:
        await message.reply("⚠️ Текущее выступление нельзя отметить как скрытое")
        return

    # Получаем следующее выступление до скрытия
    next_event_before = await db.event.get_next()

    # Переключаем статус "скрыто" для выступления
    event.hidden = not event.hidden
    await db.session.commit()

    # Выводим подтверждение
    if event.hidden:
        await message.reply(
            f"🙈 Выступление <b>{event.participant.title if event.participant else event.title}</b> скрыто"
        )
    if not event.hidden:
        await message.reply(
            f"🙉 Выступление <b>{event.participant.title if event.participant else event.title}</b> открыто"
        )

    # Получаем следующее выступление после скрытия
    next_event_after = await db.event.get_next()

    # Если скрытие повлияло на следующее по расписанию выступление - рассылаем глобальный анонс
    if next_event_after is not next_event_before:
        send_global_announcement = True
    else:
        send_global_announcement = False

    # Запускаем проверку подписок
    asyncio.create_task(
        notifier.proceed_subscriptions(
            bot=message.bot, send_global_announcement=send_global_announcement
        )
    )

    # Отправляем пользователя на страницу со скрытым/открытым выступлением
    await set_current_schedule_page(dialog_manager, event.id)
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


toggle_event_hidden_window = Window(
    Const("<b>🙈 Укажите номер выступления, которое Вы хотите скрыть/отобразить:</b>"),
    EventsList,
    SchedulePaginator,
    TextInput(
        id="toggle_event_hidden",
        type_factory=int,
        on_success=toggle_event_hidden,
        on_error=on_wrong_event_id,
    ),
    SwitchTo(state=states.SCHEDULE.MAIN, text=Const(strings.buttons.back), id="back"),
    state=states.SCHEDULE.TOGGLE_EVENT_HIDDEN,
    getter=get_schedule,
)
