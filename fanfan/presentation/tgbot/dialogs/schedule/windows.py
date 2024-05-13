from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Checkbox,
    CurrentPage,
    FirstPage,
    Group,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja

from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static.templates import schedule_list, subscriptions_list
from fanfan.presentation.tgbot.ui import strings

from .constants import (
    DATA_SEARCH_QUERY,
    ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX,
    ID_SUBSCRIPTIONS_SCROLL,
    ID_TOGGLE_HELPER_TOOLS,
)
from .getters import (
    current_event_getter,
    schedule_getter,
    subscriptions_getter,
)
from .handlers import (
    schedule_text_input_handler,
    set_next_event_handler,
    subscriptions_text_input_handler,
    toggle_all_notifications_handler,
)
from .widgets import RESET_SEARCH_BUTTON, SCHEDULE_SCROLL, SEARCH_INDICATOR

schedule_main_window = Window(
    Title(Const(strings.titles.schedule)),
    Jinja(schedule_list),
    SEARCH_INDICATOR,
    TextInput(
        id="schedule_main_window_text_input",
        type_factory=str,
        on_success=schedule_text_input_handler,
    ),
    Row(
        Checkbox(
            Const("🧰 ❌"),
            Const("🧰 Инструменты волонтёра"),
            id="id_toggle_helper_tools",
        ),
        Group(
            Button(
                text=Const("⏭️"),
                id="next_event",
                on_click=set_next_event_handler,
                when=~F["dialog_data"][DATA_SEARCH_QUERY],
            ),
            Url(
                text=Const("❓"),
                url=Const(
                    "https://fan-fan.notion.site/0781a7598cf34348866226315372c49e",
                ),
            ),
            when=F["middleware_data"]["dialog_manager"]
            .find(ID_TOGGLE_HELPER_TOOLS)
            .is_checked(),
        ),
        when=F["current_user"].role.in_([UserRole.HELPER, UserRole.ORG]) & F["events"],
    ),
    SwitchTo(
        text=Const(strings.titles.notifications),
        id="open_notifications_menu",
        state=states.SCHEDULE.SUBSCRIPTIONS,
    ),
    RESET_SEARCH_BUTTON,
    SCHEDULE_SCROLL,
    Cancel(text=Const(strings.buttons.back)),
    getter=[schedule_getter, current_event_getter, current_user_getter],
    state=states.SCHEDULE.MAIN,
)

subscriptions_main_window = Window(
    Title(Const(strings.titles.notifications)),
    Jinja(subscriptions_list),
    Const(
        "➕ <i>Чтобы подписаться, нажми на номер выступления в расписании</i>",
        when=~F["subscriptions"],
    ),
    TextInput(
        id="subscriptions_text_input",
        type_factory=str,
        on_success=subscriptions_text_input_handler,
    ),
    Button(
        Case(
            {
                True: Const("🔕 Получать только свои уведомления"),
                False: Const("🔔 Получать все уведомления"),
            },
            selector=F[CURRENT_USER].settings.receive_all_announcements,
        ),
        id=ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX,
        on_click=toggle_all_notifications_handler,
    ),
    StubScroll(ID_SUBSCRIPTIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_SUBSCRIPTIONS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.SCHEDULE.MAIN,
    ),
    getter=[subscriptions_getter, current_user_getter],
    state=states.SCHEDULE.SUBSCRIPTIONS,
)
