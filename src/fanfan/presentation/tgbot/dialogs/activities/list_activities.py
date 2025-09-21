import operator
from typing import TYPE_CHECKING, Any

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
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.activities.get_activities_page import (
    GetActivitiesPage,
    GetActivitiesPageDTO,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.activity import ActivityId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.activities.data import (
    ActivitiesDialogData,
)
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

if TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll

ID_ACTIVITIES_SCROLL = "activities_scroll"


@inject
async def list_activities_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    get_activities_page: FromDishka[GetActivitiesPage],
    **kwargs,
):
    scroll: ManagedScroll = dialog_manager.find(ID_ACTIVITIES_SCROLL)
    page = await get_activities_page(
        GetActivitiesPageDTO(
            pagination=Pagination(
                limit=current_user.settings.items_per_page,
                offset=await scroll.get_page() * current_user.settings.items_per_page,
            )
        )
    )

    pages = page.total // current_user.settings.items_per_page + bool(
        page.total % current_user.settings.items_per_page
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
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(ActivitiesDialogData)
    dialog_data.activity_id = ActivityId(item_id)
    dialog_data_adapter.flush(dialog_data)
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
