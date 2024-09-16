from aiogram import F
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
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import AsyncContainer

from fanfan.application.achievements.get_achievements_page import GetAchievementsPage
from fanfan.core.models.page import Pagination
from fanfan.core.models.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static.templates import achievements_list
from fanfan.presentation.tgbot.ui import strings

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"
DATA_USER_ID = "user_id"


async def list_achievements_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: FullUserDTO,
    **kwargs,
) -> dict:
    get_achievements_page = await container.get(GetAchievementsPage)

    page = await get_achievements_page(
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page()
            * user.settings.items_per_page,
        ),
        for_user_id=dialog_manager.start_data[DATA_USER_ID],
    )

    return {
        "achievements": page.items,
        "pages": page.total // user.settings.items_per_page
        + bool(page.total % user.settings.items_per_page),
        "showing_self": dialog_manager.start_data[DATA_USER_ID] == user.id,
    }


list_achievements_window = Window(
    Title(
        Case(
            texts={
                True: Const("🏆 Твои достижения"),
                False: Const(strings.titles.achievements),
            },
            selector="showing_self",
        ),
    ),
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
        when=F["pages"] > 1,
    ),
    Cancel(text=Const(strings.buttons.back)),
    state=states.Achievements.list_achievements,
    getter=list_achievements_getter,
)
