from aiogram import F
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import StubScroll, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from dishka import AsyncContainer
from sulguk import SULGUK_PARSE_MODE

from fanfan.application.activities.get_activity_by_id import GetActivityById
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.activities.common import (
    DATA_SELECTED_ACTIVITY_ID,
)
from fanfan.presentation.tgbot.dialogs.activities.list_activities import (
    ID_ACTIVITIES_SCROLL,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings


async def view_activity_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_activity_by_id = await container.get(GetActivityById)

    activity = await get_activity_by_id(
        dialog_manager.dialog_data[DATA_SELECTED_ACTIVITY_ID],
    )
    return {
        "title": activity.title,
        "description": activity.description,
        "subtext": activity.subtext,
        "image_path": activity.image_path,
    }


view_activity_window = Window(
    Title(Format("{title}")),
    Format("{description}"),
    Format("\n{subtext}", when=F["subtext"]),
    StaticMedia(path=Format("{image_path}"), when=F["image_path"]),
    StubScroll(id=ID_ACTIVITIES_SCROLL, pages="pages"),
    SwitchTo(
        Const(strings.buttons.back),
        "back_to_activity_selection",
        states.Activities.list_activities,
    ),
    parse_mode=SULGUK_PARSE_MODE,
    state=states.Activities.view_activity,
    getter=view_activity_getter,
)
