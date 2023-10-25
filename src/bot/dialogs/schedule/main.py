from aiogram import F
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.dialog import ChatEvent
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Checkbox,
    Group,
    ManagedCheckbox,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    EventsList,
    SchedulePaginator,
    schedule_getter,
    set_search_query,
)
from src.bot.dialogs.schedule.tools.set_next_event import set_next_event
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings


async def toggle_helper_tools(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager
):
    manager.dialog_data["helper_tools_toggle"] = checkbox.is_checked()


schedule_main_window = Window(
    Title(strings.titles.schedule),
    EventsList,
    Const(
        "🔍⌨️ <i>Отправьте поисковой запрос или номер страницы для перехода</i>",
        when=~F["dialog_data"]["search_query"],
    ),
    TextInput(
        id="SEARCH_INPUT",
        type_factory=str,
        on_success=set_search_query,
    ),
    Group(
        Group(
            Row(
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
            ),
            Row(
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
            ),
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
    SchedulePaginator,
    Cancel(text=Const(strings.buttons.back)),
    state=states.SCHEDULE.MAIN,
    getter=schedule_getter,
)
