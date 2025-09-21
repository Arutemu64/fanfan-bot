from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.schedule.management.move_event import (
    MoveEventDTO,
    MoveScheduleEvent,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    handle_schedule_text_input,
)
from fanfan.presentation.tgbot.dialogs.schedule.data import ScheduleDialogData
from fanfan.presentation.tgbot.dialogs.schedule.getters import schedule_getter
from fanfan.presentation.tgbot.dialogs.schedule.widgets.schedule_scroll import (
    SCHEDULE_SCROLL,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import schedule_list


@inject
async def move_event_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
    move_event: FromDishka[MoveScheduleEvent],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(ScheduleDialogData)
    place_after_event = await handle_schedule_text_input(dialog_manager, data)
    if place_after_event:
        result = await move_event(
            MoveEventDTO(
                event_id=dialog_data.event_id,
                place_after_event_id=place_after_event.id,
            )
        )
        await message.reply(
            f"✅ Выступление <b>{result.event.title}</b> поставлено "
            f"после <b>{result.place_after_event.title}</b>\n"
        )
        await dialog_manager.switch_to(
            states.Schedule.EVENT_DETAILS,
            show_mode=ShowMode.DELETE_AND_SEND,
        )


move_event_window = Window(
    Title(
        Const("🔃 Выберите выступление, после которого его нужно поставить"),
        upper=False,
    ),
    Jinja(schedule_list),
    TextInput(
        id="move_event_window_text_input",
        type_factory=str,
        on_success=move_event_handler,
    ),
    SwitchInlineQueryCurrentChat(
        text=Const(strings.buttons.search),
        switch_inline_query=Const(""),
    ),
    SCHEDULE_SCROLL,
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.Schedule.EVENT_DETAILS,
    ),
    getter=schedule_getter,
    state=states.Schedule.MOVE_EVENT,
)
