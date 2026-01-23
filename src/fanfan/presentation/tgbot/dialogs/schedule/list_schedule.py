from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.schedule.management.set_next_event import SetNextScheduleEvent
from fanfan.core.constants.permissions import Permissions
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.schedule.api import show_event_details
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    handle_schedule_text_input,
    show_event_page,
)
from fanfan.presentation.tgbot.dialogs.schedule.getters import (
    current_event_getter,
    helpers_schedule_getter,
    schedule_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.widgets.schedule_scroll import (
    SCHEDULE_SCROLL,
    update_schedule_handler,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import schedule_list


@inject
async def set_next_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    set_next_event: FromDishka[SetNextScheduleEvent],
) -> None:
    result = await set_next_event()
    await callback.message.answer(
        f"✅ Выступление <b>{result.current_event.title}</b> отмечено текущим\n",
    )
    await show_event_page(manager, result.current_event.id)
    manager.show_mode = ShowMode.DELETE_AND_SEND


async def list_schedule_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    event = await handle_schedule_text_input(dialog_manager, data)
    if event:
        await show_event_details(dialog_manager, event.id)


schedule_main_window = Window(
    Title(Const(strings.titles.schedule)),
    Jinja(schedule_list),
    TextInput(
        id="schedule_main_window_text_input",
        type_factory=str,
        on_success=list_schedule_input_handler,
    ),
    Button(
        text=Const("⏭️ Переключить на следующее"),
        id="next_event",
        on_click=set_next_event_handler,
        when=F[Permissions.CAN_MANAGE_SCHEDULE],
    ),
    Row(
        SwitchInlineQueryCurrentChat(
            text=Const(strings.buttons.search),
            switch_inline_query=Const(""),
        ),
        Button(
            text=Const("🔥 Сейчас"),
            id="go_to_current",
            on_click=update_schedule_handler,
            when="current_event",
        ),
        SwitchTo(
            text=Const(strings.titles.subscriptions),
            id="open_notifications_menu",
            state=states.Schedule.SUBSCRIPTIONS,
        ),
    ),
    SCHEDULE_SCROLL,
    Cancel(text=Const(strings.buttons.back)),
    getter=[
        schedule_getter,
        current_event_getter,
        helpers_schedule_getter,
    ],
    state=states.Schedule.MAIN,
)
