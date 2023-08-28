import asyncio

from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    EventsList,
    SchedulePaginator,
    get_schedule,
    set_schedule_page,
    set_search_query,
)
from src.bot.dialogs.schedule.utils import notifier
from src.bot.ui import strings
from src.db import Database


async def swap_events(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]

    if len(data.split()) == 1:
        await set_search_query(message, widget, dialog_manager, data)
        return

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

    # Получаем выступления, проверяем их существование
    event1 = await db.event.get(int(args[0]))
    event2 = await db.event.get(int(args[1]))
    if not event1 or not event2:
        await message.reply("⚠️ Пара выступлений не найдена!")
        return

    # Получаем следующее выступление до переноса
    current_event = await db.event.get_current()
    next_event_before = await db.event.get_next(current_event)

    # Не очень красиво (из-за ограничений в БД) меняем пару выступлений местами
    event1_position, event2_position = event1.position, event2.position
    event1.position, event2.position = event1.position * 10000, event2.position * 10000
    await db.session.flush([event1, event2])
    event1.position, event2.position = event2_position, event1_position
    await db.session.commit()
    await db.session.refresh(event1, ["real_position"])
    await db.session.refresh(event2, ["real_position"])

    # Выводим подтверждение
    await message.reply(
        f"✅ Выступление <b>{event1.joined_title}</b> "
        f"заменено на <b>{event2.joined_title}</b>"
    )

    # Получаем следующее выступление после переноса
    next_event_after = await db.event.get_next(current_event)

    # Если перенос повлиял на следующее выступление - рассылаем глобальный анонс
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

    # Отправляем пользователя на страницу с первым из переносимых выступлений
    await set_schedule_page(dialog_manager, event1)


swap_events_window = Window(
    Const("<b>🔃 Укажите номера двух выступлений, которые нужно поменять местами:</b>"),
    Const("""<i>(через пробел, например: "5 2")</i>\n"""),
    EventsList,
    Const(
        "🔍 <i>Для поиска отправьте запрос сообщением</i>",
        when=~F["dialog_data"]["search_query"],
    ),
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
