from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.quest.get_achievements_page import (
    GetAchievementsPage,
    GetAchievementsPageDTO,
)
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements.data import (
    AchievementsDialogData,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import achievements_list

if TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll

ID_ACHIEVEMENTS_SCROLL = "id_achievements_scroll"
ID_ADD_ACHIEVEMENT_INPUT = "id_add_achievement_input"


@inject
async def list_achievements_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    dialog_data_adapter: DialogDataAdapter,
    get_achievements_page: FromDishka[GetAchievementsPage],
    get_user_by_id: FromDishka[GetUserById],
    **kwargs,
) -> dict:
    scroll: ManagedScroll = dialog_manager.find(ID_ACHIEVEMENTS_SCROLL)
    dialog_data = dialog_data_adapter.load(AchievementsDialogData)
    page = await get_achievements_page(
        GetAchievementsPageDTO(
            pagination=Pagination(
                limit=current_user.settings.items_per_page,
                offset=await scroll.get_page() * current_user.settings.items_per_page,
            ),
            for_user_id=dialog_data.user_id,
        )
    )

    user = await get_user_by_id(dialog_data.user_id)

    pages = page.total // current_user.settings.items_per_page + bool(
        page.total % current_user.settings.items_per_page
    )

    return {
        "achievements": page.items,
        "pages": pages or 1,
        "username": user.username,
    }


list_achievements_window = Window(
    Title(Jinja("🏆 Достижения @{{ username }}")),
    Jinja(achievements_list),
    StubScroll(id=ID_ACHIEVEMENTS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACHIEVEMENTS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏭️")),
    ),
    Cancel(text=Const(strings.buttons.back)),
    state=states.Achievements.LIST_ACHIEVEMENTS,
    getter=list_achievements_getter,
)
