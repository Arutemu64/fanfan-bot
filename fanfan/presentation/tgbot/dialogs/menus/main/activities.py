import operator
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Column,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    Select,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from sulguk import SULGUK_PARSE_MODE

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_ACTIVITIES_SCROLL = "activities_scroll"

DATA_SELECTED_ACTIVITY_ID = "data_selected_activity_id"


async def activities_getter(
    dialog_manager: DialogManager, app: AppHolder, user: FullUserDTO, **kwargs
):
    page = await app.activities.get_activities_page(
        page_number=await dialog_manager.find(ID_ACTIVITIES_SCROLL).get_page(),
        activities_per_page=user.settings.items_per_page,
    )
    return {
        "activities_list": [(a.id, a.title) for a in page.items],
        "pages": page.total_pages,
    }


async def activity_info_getter(
    dialog_manager: DialogManager, app: AppHolder, user: FullUserDTO, **kwargs
):
    activity = await app.activities.get_activity(
        dialog_manager.dialog_data[DATA_SELECTED_ACTIVITY_ID]
    )
    return {
        "title": activity.title,
        "description": activity.description,
        "subtext": activity.subtext,
        "image_path": activity.image_path,
    }


async def select_activity_handler(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: int,
):
    dialog_manager.dialog_data[DATA_SELECTED_ACTIVITY_ID] = item_id
    await dialog_manager.switch_to(states.ACTIVITIES.ACTIVITY_INFO)


select_activity_window = Window(
    Title(Const(strings.titles.activities)),
    Const(
        "В этом разделе собрана вся самая необходимая "
        "и интересная информация о фестивале",
    ),
    Column(
        Select(
            Format("{item[1]}"),
            id="activity_selector",
            item_id_getter=operator.itemgetter(0),
            items="activities_list",
            type_factory=int,
            on_click=select_activity_handler,
        ),
    ),
    Row(
        FirstPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACTIVITIES_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    Cancel(Const(strings.buttons.back)),
    getter=activities_getter,
    state=states.ACTIVITIES.SELECT_ACTIVITY,
)


activity_info_window = Window(
    Title(Format("{title}")),
    Format("{description}"),
    Format("\n{subtext}", when=F["subtext"]),
    StaticMedia(path=Format("{image_path}"), when=F["image_path"]),
    StubScroll(id=ID_ACTIVITIES_SCROLL, pages="pages"),
    SwitchTo(
        Const(strings.buttons.back),
        "back_to_activity_selection",
        states.ACTIVITIES.SELECT_ACTIVITY,
    ),
    parse_mode=SULGUK_PARSE_MODE,
    state=states.ACTIVITIES.ACTIVITY_INFO,
    getter=activity_info_getter,
)

dialog = Dialog(
    select_activity_window,
    activity_info_window,
)
