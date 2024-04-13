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
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_ACTIVITIES_SCROLL = "activities_scroll"


async def activity_getter(dialog_manager: DialogManager, app: AppHolder, **kwargs):
    page = await app.common.get_activity_page(
        await dialog_manager.find(ID_ACTIVITIES_SCROLL).get_page(),
    )
    activity = page.items[0]
    return {
        "title": activity.title,
        "description": activity.description,
        "subtext": activity.subtext,
        "image_path": activity.image_path,
        "pages": page.total_pages,
    }


activity_window = Window(
    Title(Format("{title}")),
    Format("{description}"),
    Format("\n{subtext}", when=F["subtext"]),
    StaticMedia(path=Format("{image_path}"), when=F["image_path"]),
    StubScroll(id=ID_ACTIVITIES_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACTIVITIES_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("⏭️")),
        when=F["activity"],
    ),
    SwitchTo(Const(strings.buttons.back), "main_menu", states.MAIN.HOME),
    state=states.MAIN.ACTIVITIES,
    getter=activity_getter,
)
