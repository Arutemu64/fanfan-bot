from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Checkbox,
    Group,
    Start,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Const

from fanfan.config import conf
from fanfan.presentation.tgbot.dialogs import (
    states,
)
from fanfan.presentation.tgbot.dialogs.menus.schedule.common import (
    ID_SCHEDULE_SCROLL,
    SEARCH_QUERY,
    ScheduleWindow,
    set_search_query_handler,
)
from fanfan.presentation.tgbot.dialogs.menus.schedule.tools.set_next_event import (
    set_next_event_handler,
)
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_TOGGLE_HELPER_TOOLS = "toggle_helper_tools"


async def set_page_handler(
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
        when=~F["dialog_data"][SEARCH_QUERY],
    ),
    before_paginator=Group(
        Group(
            Group(
                Button(
                    text=Const("⏭️ Следующее"),
                    id="next_event",
                    on_click=set_next_event_handler,
                    when=~F["dialog_data"][SEARCH_QUERY],
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
                    url=Const(str(conf.bot.docs_link)),
                ),
                width=2,
                when=F["middleware_data"]["dialog_manager"]
                .find(ID_TOGGLE_HELPER_TOOLS)
                .is_checked(),
            ),
            Checkbox(
                Const("🧰 ⬇️ Инструменты волонтёра"),
                Const("🧰 ⬆️ Инструменты волонтёра"),
                id="toggle_helper_tools",
            ),
            when=F["is_helper"] & F["events"],
        ),
        Start(
            text=Const(strings.titles.notifications),
            id="open_notifications_menu",
            state=states.SUBSCRIPTIONS.MAIN,
        ),
    ),
    after_paginator=Cancel(text=Const(strings.buttons.back)),
    text_input=TextInput(
        id="schedule_main_window_input",
        type_factory=int,
        on_success=set_page_handler,
        on_error=set_search_query_handler,
    ),
)
