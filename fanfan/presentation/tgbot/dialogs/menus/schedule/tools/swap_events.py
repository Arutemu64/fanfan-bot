from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.menus.schedule.common import (
    ID_SCHEDULE_SCROLL,
    SEARCH_QUERY,
    ScheduleWindow,
    show_event_page,
)
from fanfan.presentation.tgbot.dialogs.widgets import Title, get_delete_delivery_button
from fanfan.presentation.tgbot.ui import strings


async def swap_events_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]

    # Поиск
    if len(data.split()) == 1:
        dialog_manager.dialog_data[SEARCH_QUERY] = data
        scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
        await scroll.set_page(0)
        return

    # Проверяем, что номера выступлений введены верно
    args = data.split()
    if len(args) != 2:
        await message.reply("⚠️ Вы должны указать два выступления!")
        return
    if not (args[0].isnumeric() and args[1].isnumeric()):
        await message.reply("⚠️ Неверно указаны номера выступлений!")
        return

    try:
        event1, event2, delivery_info = await app.schedule_mgmt.swap_events(
            int(args[0]), int(args[1])
        )
    except ServiceError as e:
        await message.reply(e.message)
        return

    await message.reply(
        f"✅ Выступление <b>{event1.title}</b> заменено на <b>{event2.title}</b>"
        f"Будет отправлено {delivery_info.count} "
        f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n",
        reply_markup=InlineKeyboardBuilder(
            [[get_delete_delivery_button(delivery_info.delivery_id)]]
        ).as_markup(),
    )
    await show_event_page(dialog_manager, event1.id)


swap_events_window = ScheduleWindow(
    state=states.SCHEDULE.SWAP_EVENTS,
    header=Title(
        Const("🔃 Укажите номера двух выступлений, которые нужно поменять местами:"),
        upper=False,
        subtitle=Const("""(через пробел, например: "5 2")"""),
    ),
    after_paginator=SwitchTo(
        state=states.SCHEDULE.MAIN,
        text=Const(strings.buttons.back),
        id="back",
    ),
    text_input=TextInput(
        id="swap_events_window_input",
        type_factory=str,
        on_success=swap_events_handler,
    ),
)
