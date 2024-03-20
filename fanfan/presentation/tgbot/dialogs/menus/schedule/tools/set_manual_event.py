from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import (
    states,
)
from fanfan.presentation.tgbot.dialogs.menus.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.menus.schedule.common import (
    ScheduleWindow,
    set_search_query_handler,
)
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings


async def set_manual_event_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]

    try:
        event = await app.schedule_mgmt.set_current_event(data)
    except ServiceError as e:
        await message.reply(e.message)
        return

    await message.reply(f"✅ Выступление <b>{event.title}</b> отмечено как текущее")
    await show_event_page(dialog_manager, event.id)
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


set_manual_event_window = ScheduleWindow(
    state=states.SCHEDULE.ASK_MANUAL_EVENT,
    header=Title(
        Const("🔢 Укажите номер выступления, которое хотите отметить текущим:"),
        upper=False,
    ),
    after_paginator=SwitchTo(
        state=states.SCHEDULE.MAIN, text=Const(strings.buttons.back), id="back"
    ),
    text_input=TextInput(
        id="manual_event_input",
        type_factory=int,
        on_success=set_manual_event_handler,
        on_error=set_search_query_handler,
    ),
)
