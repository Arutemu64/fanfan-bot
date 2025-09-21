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

from fanfan.presentation.tgbot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    get_current_event,
    show_event_page,
)


async def update_schedule_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    if current_event := await get_current_event(manager):
        await show_event_page(manager, current_event.id)


SCHEDULE_SCROLL = Group(
    Row(
        StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
        FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
        Button(
            text=Format(text="{page} 🔥"),
            id="update_schedule",
            on_click=update_schedule_handler,
        ),
        NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SCHEDULE_SCROLL, text=Format("⏭️")),
    ),
)
