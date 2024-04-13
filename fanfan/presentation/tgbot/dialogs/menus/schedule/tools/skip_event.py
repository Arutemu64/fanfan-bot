from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input.text import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot.dialogs import (
    states,
)
from fanfan.presentation.tgbot.dialogs.menus.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.menus.schedule.common import (
    ScheduleWindow,
    set_search_query_handler,
)
from fanfan.presentation.tgbot.dialogs.widgets import Title, get_delete_delivery_button
from fanfan.presentation.tgbot.ui import strings


async def skip_event_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]

    try:
        event, delivery_info = await app.schedule_mgmt.skip_event(data)
        if event.skip:
            text = f"🙈 Выступление <b>{event.title}</b> пропущено\n"
            f"Будет отправлено {delivery_info.count} "
            f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
        else:
            text = f"🙉 Выступление <b>{event.title}</b> возвращено\n"
            f"Будет отправлено {delivery_info.count} "
            f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
        await message.reply(
            text,
            reply_markup=InlineKeyboardBuilder(
                [[get_delete_delivery_button(delivery_info.delivery_id)]]
            ).as_markup()
            if delivery_info.count > 0
            else None,
        )
        await show_event_page(dialog_manager, event.id)
    except ServiceError as e:
        await message.reply(e.message)


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
