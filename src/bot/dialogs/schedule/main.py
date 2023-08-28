from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Row, StubScroll, SwitchTo
from aiogram_dialog.widgets.text import Case, Const

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    EventsList,
    SchedulePaginator,
    get_schedule,
    set_search_query,
)
from src.bot.dialogs.schedule.tools.set_next_event import set_next_event
from src.bot.ui import strings


async def toggle_helper_tools(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    toggle = manager.dialog_data.get("helper_tools_toggle")
    if toggle is True:
        manager.dialog_data["helper_tools_toggle"] = False
    else:
        manager.dialog_data["helper_tools_toggle"] = True


schedule_main_window = Window(
    Const("<b>📅 Расписание</b>\n"),
    EventsList,
    Const(
        "🔍 <i>Для поиска отправьте запрос сообщением</i>",
        when=~F["dialog_data"]["search_query"],
    ),
    TextInput(
        id="SEARCH_INPUT",
        type_factory=str,
        on_success=set_search_query,
    ),
    StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
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
                text=Const("🙈 Скрыть/отобразить"),
                id="hide_events",
                state=states.SCHEDULE.TOGGLE_EVENT_HIDDEN,
            ),
        ),
        when=F["dialog_data"]["helper_tools_toggle"],
    ),
    Button(
        text=Case(
            texts={
                True: Const("🧰 ⬇️ Инструменты волонтёра"),
                False: Const("🧰 ⬆️ Инструменты волонтёра"),
                None: Const("🧰 ⬆️ Инструменты волонтёра"),
            },
            selector=F["dialog_data"]["helper_tools_toggle"],
        ),
        id="toggle_helper_tools",
        on_click=toggle_helper_tools,
        when=F["is_helper"] & F["events"],
    ),
    SwitchTo(
        text=Const("🔔 Уведомления"),
        state=states.SCHEDULE.SUBSCRIPTIONS_MANAGEMENT,
        id="open_notifications_menu",
    ),
    SchedulePaginator,
    Cancel(text=Const(strings.buttons.back)),
    state=states.SCHEDULE.MAIN,
    getter=get_schedule,
)
