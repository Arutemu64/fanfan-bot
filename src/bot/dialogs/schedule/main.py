from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.dialog import ChatEvent
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Checkbox,
    Group,
    ManagedCheckbox,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    ScheduleWindow,
    set_search_query,
)
from src.bot.dialogs.schedule.tools.set_next_event import set_next_event
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings


async def toggle_helper_tools(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager
):
    manager.dialog_data["helper_tools_toggle"] = checkbox.is_checked()


async def set_page(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    if 0 <= data - 1 < dialog_manager.dialog_data["pages"]:
        await scroll.set_page(data - 1)


schedule_main_window = ScheduleWindow(
    state=states.SCHEDULE.MAIN,
    header=Title(Const(strings.titles.schedule)),
    footer=Const(
        "🔍⌨️ <i>Отправьте поисковой запрос или номер страницы</i>",
        when=~F["dialog_data"]["search_query"],
    ),
    before_paginator=Group(
        Group(
            Group(
                Button(
                    text=Const("⏭️ Следующее"),
                    id="next_event",
                    on_click=set_next_event,
                    when=~F["dialog_data"]["search_query"],
                ),
                SwitchTo(
                    text=Const("🔢 Указать вручную"),
                    id="manual_event",
                    state=states.SCHEDULE.ASK_MANUAL_EVENT,
                ),
                SwitchTo(
                    text=Const("🔃 Поменять местами"),
                    id="swap_events",
                    state=states.SCHEDULE.SWAP_EVENTS,
                ),
                SwitchTo(
                    text=Const("🙈 Пропустить/вернуть"),
                    id="skip_events",
                    state=states.SCHEDULE.TOGGLE_EVENT_SKIP,
                ),
                Url(
                    text=Const(strings.buttons.help),
                    url=Const(
                        "https://www.notion.so/arutemu64/d4dcc186f40f4b11b05a814e61d64140"
                    ),
                ),
                width=2,
                when=F["dialog_data"]["helper_tools_toggle"],
            ),
            Checkbox(
                Const("🧰 ⬇️ Инструменты волонтёра"),
                Const("🧰 ⬆️ Инструменты волонтёра"),
                id="toggle_helper_tools",
                on_state_changed=toggle_helper_tools,
            ),
            when=F["is_helper"] & F["events"],
        ),
        SwitchTo(
            text=Const(strings.titles.notifications),
            id="open_notifications_menu",
            state=states.SCHEDULE.SUBSCRIPTIONS_MAIN,
        ),
    ),
    after_paginator=Cancel(text=Const(strings.buttons.back)),
    text_input=TextInput(
        id="schedule_main_window_input",
        type_factory=int,
        on_success=set_page,
        on_error=set_search_query,
    ),
)
