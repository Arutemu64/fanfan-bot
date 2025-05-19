from aiogram import F
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import StubScroll, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from dishka import AsyncContainer

from fanfan.application.activities.read_activity_by_id import ReadActivityById
from fanfan.core.utils.html import sanitize_html
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.activities.common import (
    DATA_SELECTED_ACTIVITY_ID,
)
from fanfan.presentation.tgbot.dialogs.activities.list_activities import (
    ID_ACTIVITIES_SCROLL,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def view_activity_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_activity_by_id: ReadActivityById = await container.get(ReadActivityById)

    activity = await get_activity_by_id(
        dialog_manager.dialog_data[DATA_SELECTED_ACTIVITY_ID],
    )
    return {
        "title": activity.title,
        "description": sanitize_html(activity.description),
        "image_path": activity.image_path,
    }


view_activity_window = Window(
    Title(Format("{title}")),
    Format("{description}"),
    StaticMedia(path=Format("{image_path}"), when=F["image_path"]),
    StubScroll(id=ID_ACTIVITIES_SCROLL, pages="pages"),
    SwitchTo(
        Const(strings.buttons.back),
        "back_to_activity_selection",
        states.Activities.LIST_ACTIVITIES,
    ),
    state=states.Activities.VIEW_ACTIVITY,
    getter=view_activity_getter,
)
