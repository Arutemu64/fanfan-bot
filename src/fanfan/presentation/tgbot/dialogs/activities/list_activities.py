import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
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
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import AsyncContainer

from fanfan.application.activities.read_activities_page import ReadActivitiesPage
from fanfan.core.dto.page import Pagination
from fanfan.core.models.user import UserData
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.activities.common import (
    DATA_SELECTED_ACTIVITY_ID,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

ID_ACTIVITIES_SCROLL = "activities_scroll"


async def list_activities_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
):
    get_activities_page: ReadActivitiesPage = await container.get(ReadActivitiesPage)

    page = await get_activities_page(
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await dialog_manager.find(ID_ACTIVITIES_SCROLL).get_page()
            * user.settings.items_per_page,
        ),
    )

    pages = page.total // user.settings.items_per_page + bool(
        page.total % user.settings.items_per_page
    )

    return {
        "activities_list": [(a.id, a.title) for a in page.items],
        "pages": pages or 1,
    }


async def select_activity_handler(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: int,
) -> None:
    dialog_manager.dialog_data[DATA_SELECTED_ACTIVITY_ID] = item_id
    await dialog_manager.switch_to(states.Activities.VIEW_ACTIVITY)


list_activities_window = Window(
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
    ),
    Cancel(Const(strings.buttons.back)),
    getter=list_activities_getter,
    state=states.Activities.LIST_ACTIVITIES,
)
