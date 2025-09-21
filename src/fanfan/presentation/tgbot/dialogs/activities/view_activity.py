from aiogram import F
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import StubScroll, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sulguk import SULGUK_PARSE_MODE

from fanfan.application.activities.get_activity_by_id import GetActivityById
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.activities.data import (
    ActivitiesDialogData,
)
from fanfan.presentation.tgbot.dialogs.activities.list_activities import (
    ID_ACTIVITIES_SCROLL,
)
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


@inject
async def view_activity_getter(
    dialog_manager: DialogManager,
    get_activity_by_id: FromDishka[GetActivityById],
    **kwargs,
):
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(ActivitiesDialogData)

    activity = await get_activity_by_id(dialog_data.activity_id)
    return {
        "title": activity.title,
        "description": activity.description,
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
    parse_mode=SULGUK_PARSE_MODE,
)
