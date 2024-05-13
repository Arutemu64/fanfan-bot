import operator

from aiogram import F
from aiogram_dialog import Window
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

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

from .constants import ID_ACTIVITIES_SCROLL
from .getters import activities_getter, activity_info_getter
from .handlers import select_activity_handler

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
