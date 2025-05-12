import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import (
    Button,
    FirstPage,
    Group,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
)
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.schedule.get_current_event import GetCurrentEvent
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    show_event_page,
)

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def update_schedule_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_current_event: GetCurrentEvent = await container.get(GetCurrentEvent)

    if current_event := await get_current_event():
        await show_event_page(manager, current_event.id)


SCHEDULE_SCROLL = Group(
    Row(
        StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
        FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
        Button(
            text=Format(text="{page_number} 🔥"),
            id="update_schedule",
            on_click=update_schedule_handler,
        ),
        NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SCHEDULE_SCROLL, text=Format("⏭️")),
    ),
)
