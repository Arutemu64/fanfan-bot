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
    on_wrong_event_id,
)
from src.bot.dialogs.schedule.search import reset_search
from src.bot.dialogs.schedule.subscriptions import (
    SUBSCRIBE_EVENT_ID_INPUT,
    check_subscription,
)
from src.bot.dialogs.schedule.tools.set_next_event import set_next_event
from src.bot.ui import strings
from src.db import Database
from src.db.models import User


async def toggle_helper_tools(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    toggle = manager.dialog_data.get("helper_tools_toggle")
    if toggle is True:
        manager.dialog_data["helper_tools_toggle"] = False
    else:
        manager.dialog_data["helper_tools_toggle"] = True


async def toggle_all_notifications(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: User = manager.middleware_data["user"]
    db: Database = manager.middleware_data["db"]
    user.receive_all_announcements = not user.receive_all_announcements
    await db.session.flush([user])
    await db.session.commit()


schedule_main_window = Window(
    Const("<b>📅 Расписание</b>"),
    EventsList,
    Const(
        "Чтобы подписаться на выступление (или отписаться), отправьте его номер 👇",
        when="events",
    ),
    TextInput(
        id=SUBSCRIBE_EVENT_ID_INPUT,
        type_factory=int,
        on_success=check_subscription,
        on_error=on_wrong_event_id,
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
    Button(
        text=Case(
            texts={
                True: Const("🔕 Получать только свои уведомления"),
                False: Const("🔔 Получать все уведомления"),
            },
            selector=F["receive_all_announcements"],
        ),
        on_click=toggle_all_notifications,
        id="receive_all_announcements",
    ),
    SwitchTo(
        text=Const("🔍 Поиск"),
        id="search_button",
        state=states.SCHEDULE.SEARCH,
        when=~F["dialog_data"]["search_query"],
    ),
    Button(
        text=Const("🔍❌ Сбросить поиск"),
        id="reset_search",
        on_click=reset_search,
        when=F["dialog_data"]["search_query"],
    ),
    SchedulePaginator,
    Cancel(text=Const(strings.buttons.back)),
    state=states.SCHEDULE.MAIN,
    getter=get_schedule,
)
