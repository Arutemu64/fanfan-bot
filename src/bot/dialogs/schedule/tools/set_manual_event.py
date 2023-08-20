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
    ID_SCHEDULE_SCROLL,
    EventsList,
    SchedulePaginator,
    get_events_query_terms,
    get_schedule,
    on_wrong_event_id,
    set_current_schedule_page,
)
from src.bot.dialogs.schedule.tools.common import throttle_announcement
from src.bot.ui import strings
from src.bot.utils import notifier
from src.db import Database
from src.db.models import Event


async def set_manual_event(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    # Таймаут рассылки анонсов
    if await throttle_announcement(dialog_manager.middleware_data["settings"]):
        pass
    else:
        await message.answer(strings.errors.announce_too_fast)
        return

    # Сброс текущего выступления
    if data == 0:
        current_event = await db.event.get_current()
        if current_event:
            current_event.current = None
            await db.session.commit()
        await message.reply("✅ Текущее выступление сброшено!")
        await dialog_manager.find(ID_SCHEDULE_SCROLL).set_page(0)
        await dialog_manager.switch_to(states.SCHEDULE.MAIN)
        return

    # Проверяем, что выступление существует (с учётом поиска) и не скрыто
    terms = get_events_query_terms(True, dialog_manager.dialog_data.get("search_query"))
    new_current_event = await db.event.get_by_where(and_(Event.id == data, *terms))
    if not new_current_event:
        text = "⚠️ Выступление не найдено!"
        if dialog_manager.dialog_data.get("search_query"):
            text += "\n(убедитесь, что оно входит в результаты поиска)"
        await message.reply(text)
        return
    if new_current_event.hidden:
        await message.reply("⚠️ Скрытое выступление нельзя отметить как текущее!")
        return

    # Получаем текущее выступление и снимаем с него флаг "текущее"
    current_event = await db.event.get_current()
    if current_event:
        if current_event == new_current_event:
            await message.reply("⚠️ Это выступление уже отмечено как текущее!")
            return
        else:
            current_event.current = None
            await db.session.flush([current_event])

    # Отмечаем выступление как текущее
    new_current_event.current = True
    await db.session.commit()

    # Выводим подтверждение
    await message.reply(
        f"✅ Выступление <b>{new_current_event.participant.title if new_current_event.participant else new_current_event.title}</b> "
        f"отмечено как текущее"
    )

    # Запускаем проверку подписок
    asyncio.create_task(
        notifier.proceed_subscriptions(bot=message.bot, send_global_announcement=True)
    )

    # Отправляем пользователя на страницу с текущим выступлением
    await set_current_schedule_page(dialog_manager, new_current_event.id)
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


set_manual_event_window = Window(
    Const("<b>🔢 Укажите номер выступления, которое хотите отметить текущим:</b>"),
    Const("<i>(0 - сброс текущего выступления)</i>"),
    EventsList,
    SchedulePaginator,
    TextInput(
        id="manual_event_input",
        type_factory=int,
        on_success=set_manual_event,
        on_error=on_wrong_event_id,
    ),
    SwitchTo(state=states.SCHEDULE.MAIN, text=Const(strings.buttons.back), id="back"),
    state=states.SCHEDULE.ASK_MANUAL_EVENT,
    getter=get_schedule,
)
