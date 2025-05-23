import typing

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Checkbox,
    Column,
    Group,
    Row,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import AsyncContainer

from fanfan.adapters.config.models import Configuration
from fanfan.application.schedule.management.set_next_event import SetNextScheduleEvent
from fanfan.application.schedule.read_event_by_public_id import (
    ReadScheduleEventByPublicId,
)
from fanfan.core.vo.schedule_event import ScheduleEventPublicId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    CAN_EDIT_SCHEDULE,
    DATA_TOTAL_PAGES,
    ID_SCHEDULE_SCROLL,
    can_edit_schedule_getter,
    current_event_getter,
    schedule_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.view_event import show_event_details
from fanfan.presentation.tgbot.dialogs.schedule.widgets.schedule_scroll import (
    SCHEDULE_SCROLL,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import schedule_list

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll

ID_TOGGLE_HELPER_TOOLS = "toggle_helper_tools"


async def view_schedule_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    config: Configuration = await container.get(Configuration)
    return {
        "docs_link": config.docs_link,
    }


async def set_next_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    set_next_event: SetNextScheduleEvent = await container.get(SetNextScheduleEvent)

    data = await set_next_event()
    await callback.message.answer(
        f"✅ Выступление <b>{data.current_event.title}</b> отмечено текущим\n",
    )
    await show_event_page(manager, data.current_event.id)
    manager.show_mode = ShowMode.DELETE_AND_SEND


async def schedule_text_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    schedule_scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    if "/" in data and data.replace("/", "").isnumeric():
        # User clicked public ID
        public_event_id = ScheduleEventPublicId(int(data.replace("/", "")))
        get_event_id_by_public_id = await container.get(ReadScheduleEventByPublicId)
        event = await get_event_id_by_public_id(public_event_id)
        await show_event_details(dialog_manager, event.id)
    elif (
        data.isnumeric()
        and 1 <= int(data) <= dialog_manager.dialog_data[DATA_TOTAL_PAGES]
    ):
        await schedule_scroll.set_page(int(data) - 1)


schedule_main_window = Window(
    Title(Const(strings.titles.schedule)),
    Jinja(schedule_list),
    Const("👆 Нажми на номер, чтобы выбрать выступление"),
    TextInput(
        id="schedule_main_window_text_input",
        type_factory=str,
        on_success=schedule_text_input_handler,
    ),
    Column(
        Group(
            Button(
                text=Const("⏭️ Переключить на следующее"),
                id="next_event",
                on_click=set_next_event_handler,
            ),
            Url(
                text=Const("❓ Справка"),
                url=Format("{docs_link}"),
                when="docs_link",
            ),
            when=F["middleware_data"]["dialog_manager"]
            .find(ID_TOGGLE_HELPER_TOOLS)
            .is_checked(),
        ),
        Checkbox(
            Const("🧰 Инструменты волонтёра ⬇️"),
            Const("🧰 Инструменты волонтёра ⬆️"),
            id=ID_TOGGLE_HELPER_TOOLS,
        ),
        when=F[CAN_EDIT_SCHEDULE],
    ),
    Row(
        SwitchInlineQueryCurrentChat(
            text=Const(strings.buttons.search),
            switch_inline_query=Const(""),
        ),
        SwitchTo(
            text=Const(strings.titles.notifications),
            id="open_notifications_menu",
            state=states.Schedule.SUBSCRIPTIONS,
        ),
    ),
    SCHEDULE_SCROLL,
    Cancel(text=Const(strings.buttons.back)),
    getter=[
        schedule_getter,
        current_event_getter,
        view_schedule_getter,
        can_edit_schedule_getter,
    ],
    state=states.Schedule.MAIN,
)
