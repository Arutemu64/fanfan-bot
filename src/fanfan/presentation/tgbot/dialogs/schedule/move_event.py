import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from fanfan.application.schedule.management.move_event import (
    MoveEventDTO,
    MoveScheduleEvent,
)
from fanfan.application.schedule.read_event_by_public_id import (
    ReadScheduleEventByPublicId,
)
from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    DATA_SELECTED_EVENT_ID,
    schedule_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.widgets.schedule_scroll import (
    SCHEDULE_SCROLL,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import schedule_list

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def move_event_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    get_event_by_public_id = await container.get(ReadScheduleEventByPublicId)
    move_event: MoveScheduleEvent = await container.get(MoveScheduleEvent)

    if "/" in data and data.replace("/", "").isnumeric():
        event_id = ScheduleEventId(dialog_manager.start_data[DATA_SELECTED_EVENT_ID])
        place_after_event_public_id = ScheduleEventPublicId(int(data.replace("/", "")))
        place_after_event = await get_event_by_public_id(place_after_event_public_id)
        data = await move_event(
            MoveEventDTO(event_id=event_id, place_after_event_id=place_after_event.id)
        )
        await message.reply(
            f"✅ Выступление <b>{data.event.title}</b> поставлено "
            f"после <b>{data.place_after_event.title}</b>\n"
        )
        await dialog_manager.switch_to(
            states.Schedule.EVENT_DETAILS,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
    elif data.isnumeric():
        await show_event_page(dialog_manager, ScheduleEventId(int(data)))


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
