from typing import Optional

from aiogram import F
from aiogram_dialog import Dialog, DialogManager, Window
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

from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.static.templates import achievements_list
from fanfan.presentation.tgbot.ui import strings

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"
DATA_USER_ID = "data_user_id"


async def achievements_getter(
    dialog_manager: DialogManager,
    app: AppHolder,
    **kwargs,
):
    user = await app.users.get_user_by_id(dialog_manager.dialog_data[DATA_USER_ID])
    page = await app.quest.get_achievements_page(
        page_number=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page(),
        achievements_per_page=user.settings.items_per_page,
        user_id=user.id,
    )
    return {
        "achievements": page.items,
        "pages": page.total_pages,
        "showing_self": user.id == dialog_manager.event.from_user.id,
    }


async def on_start_achievements(start_data: Optional[int], manager: DialogManager):
    manager.dialog_data[DATA_USER_ID] = start_data or manager.event.from_user.id


achievements_window = Window(
    Title(
        Case(
            texts={
                True: Const("🏆 Ваши достижения"),
                False: Const(strings.titles.achievements),
            },
            selector="showing_self",
        )
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
    state=states.ACHIEVEMENTS.MAIN,
    getter=achievements_getter,
)

dialog = Dialog(achievements_window, on_start=on_start_achievements)
