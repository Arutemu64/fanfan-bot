from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input.text import ManagedTextInput, TextInput
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


async def skip_event_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]

    try:
        event = await app.schedule_mgmt.skip_event(data)
    except ServiceError as e:
        await message.reply(e.message)
        return

    if event.skip:
        await message.reply(f"🙈 Выступление <b>{event.title}</b> пропущено")
    if not event.skip:
        await message.reply(f"🙉 Выступление <b>{event.title}</b> возвращено")
    await show_event_page(dialog_manager, event.id)


toggle_event_skip_window = ScheduleWindow(
    state=states.SCHEDULE.TOGGLE_EVENT_SKIP,
    header=Title(
        Const("🙈 Укажите номер выступления, которое Вы хотите скрыть/отобразить:"),
        upper=False,
    ),
    after_paginator=SwitchTo(
        state=states.SCHEDULE.MAIN,
        text=Const(strings.buttons.back),
        id="back",
    ),
    text_input=TextInput(
        id="toggle_event_skip_window_input",
        type_factory=int,
        on_success=skip_event_handler,
        on_error=set_search_query_handler,
    ),
)
