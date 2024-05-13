from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja

from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import current_user_getter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.schedule.event_details.getters import (
    selected_event_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.event_details.handlers import (
    move_event_handler,
    set_as_current,
    set_counter_handler,
    skip_event,
    unsubscribe_button_handler,
)
from fanfan.presentation.tgbot.dialogs.schedule.getters import (
    current_event_getter,
    schedule_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.widgets import (
    RESET_SEARCH_BUTTON,
    SCHEDULE_SCROLL,
    SEARCH_INDICATOR,
)
from fanfan.presentation.tgbot.static.templates import (
    schedule_list,
    selected_event_info,
)
from fanfan.presentation.tgbot.ui import strings

selected_event_window = Window(
    Title(Const("🎭 Выступление")),
    Jinja(selected_event_info),
    Const("Что ты хочешь сделать с этим выступлением?"),
    SwitchTo(
        text=Const("🔔 Подписаться"),
        id="subscribe",
        state=states.EVENT_DETAILS.SET_SUBSCRIPTION_COUNTER,
        when=~F["selected_event"].user_subscription,
    ),
    Button(
        text=Const("🔕 Отписаться"),
        id="unsubscribe",
        on_click=unsubscribe_button_handler,
        when=F["selected_event"].user_subscription,
    ),
    Group(
        Button(
            text=Const("🎬 Отметить текущим"),
            id="set_as_current",
            on_click=set_as_current,
            when=~F["selected_event"].current & ~F["selected_event"].skip,
        ),
        SwitchTo(
            text=Const("🔀 Переместить"),
            id="move_event",
            state=states.EVENT_DETAILS.MOVE_EVENT,
        ),
        Button(
            text=Case(
                texts={False: Const("🙈 Пропустить"), True: Const("🙉 Вернуть")},
                selector=F["selected_event"].skip,
            ),
            id="skip_event",
            on_click=skip_event,
            when=~F["selected_event"].current,
        ),
        when=F["current_user"].role.in_([UserRole.HELPER, UserRole.ORG]),
    ),
    Cancel(Const(strings.buttons.back)),
    getter=[selected_event_getter, current_user_getter, current_event_getter],
    state=states.EVENT_DETAILS.MAIN,
)
move_event_window = Window(
    Title(
        Const("🔃 Выберите выступление, после которого его нужно поставить"),
        upper=False,
    ),
    Jinja(schedule_list),
    SEARCH_INDICATOR,
    TextInput(
        id="move_event_window_text_input",
        type_factory=str,
        on_success=move_event_handler,
    ),
    RESET_SEARCH_BUTTON,
    SCHEDULE_SCROLL,
    SwitchTo(
        text=Const(strings.buttons.back), id="back", state=states.EVENT_DETAILS.MAIN
    ),
    getter=[schedule_getter, current_event_getter],
    state=states.EVENT_DETAILS.MOVE_EVENT,
)
set_subscription_counter_window = Window(
    Format(
        "🔢 За сколько выступлений до начала " "начать присылать уведомления?",
    ),
    TextInput(
        id="counter_input",
        type_factory=int,
        on_success=set_counter_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back), id="back", state=states.EVENT_DETAILS.MAIN
    ),
    getter=selected_event_getter,
    state=states.EVENT_DETAILS.SET_SUBSCRIPTION_COUNTER,
)
