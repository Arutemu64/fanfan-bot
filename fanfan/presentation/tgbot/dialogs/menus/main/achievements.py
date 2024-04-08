from aiogram import F
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.static.templates import achievements_list
from fanfan.presentation.tgbot.ui import strings

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"


async def achievements_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    page = await app.quest.get_achievements_page(
        page_number=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page(),
        achievements_per_page=user.items_per_page,
        user_id=user.id,
    )
    return {
        "achievements": page.items,
        "pages": page.total_pages,
    }


achievements_window = Window(
    Title(Const(strings.titles.achievements)),
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
    SwitchTo(text=Const(strings.buttons.back), state=states.MAIN.HOME, id="back"),
    state=states.MAIN.ACHIEVEMENTS,
    getter=achievements_getter,
)
