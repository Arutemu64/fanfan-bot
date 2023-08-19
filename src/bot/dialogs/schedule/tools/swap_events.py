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
    set_current_schedule_page,
)
from src.bot.ui import strings
from src.bot.utils import notifier
from src.db import Database
from src.db.models import Event


async def swap_events(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    # Проверяем, что номера выступлений введены верно
    args = data.split()
    if len(args) != 2:
        await message.reply("⚠️ Вы должны указать два выступления!")
        return
    if not (args[0].isnumeric() and args[1].isnumeric()):
        await message.reply("⚠️ Неверно указаны номера выступлений!")
        return
    if args[0] == args[1]:
        await message.reply("⚠️ Номера выступлений не могут совпадать!")
        return

    db: Database = dialog_manager.middleware_data["db"]

    # Получаем выступления (с учётом поиска), проверяем их существование
    terms = get_events_query_terms(True, dialog_manager.dialog_data.get("search_query"))
    event1 = await db.event.get_by_where(and_(Event.id == int(args[0]), *terms))
    event2 = await db.event.get_by_where(and_(Event.id == int(args[1]), *terms))
    if not event1 or not event2:
        text = "⚠️ Пара выступлений не найдена!"
        if dialog_manager.dialog_data.get("search_query"):
            text += "\n(убедитесь, что она входит в результаты поиска)"
        await message.reply(text)
        return

    # Не очень красиво (из-за ограничений в БД) меняем пару выступлений местами
    event1_position, event2_position = event1.position, event2.position
    event1.position, event2.position = event1.position * 10000, event2.position * 10000
    await db.session.flush([event1, event2])
    event1.position, event2.position = event2_position, event1_position
    await db.session.flush([event1, event2])
    await db.session.commit()

    # Выводим подтверждение
    await message.reply(
        f"✅ Выступление <b>{event1.participant.title if event1.participant else event1.title}</b> заменено "
        f"на <b>{event2.participant.title if event2.participant else event2.title}</b>"
    )

    # Получаем текущее выступление
    current_event = await db.event.get_current()

    # Если перенос повлиял на текущее или следующее выступления - рассылаем глобальный анонс
    if (event1.position in [current_event.position, current_event.position + 1]) or (
        event2.position in [current_event.position, current_event.position + 1]
    ):
        send_global_announcement = True
    else:
        send_global_announcement = False

    # Запускаем проверку подписок
    asyncio.create_task(
        notifier.proceed_subscriptions(
            bot=message.bot, send_global_announcement=send_global_announcement
        )
    )

    # Отправляем пользователя на страницу с первым из переносимых выступлений
    await set_current_schedule_page(dialog_manager, event1.id)
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


swap_events_window = Window(
    Const("<b>🔃 Укажите номера двух выступлений, которые нужно поменять местами:</b>"),
    EventsList,
    SchedulePaginator,
    TextInput(
        id="swap_events_input",
        type_factory=str,
        on_success=swap_events,
    ),
    SwitchTo(state=states.SCHEDULE.MAIN, text=Const(strings.buttons.back), id="back"),
    state=states.SCHEDULE.SWAP_EVENTS,
    getter=get_schedule,
)
