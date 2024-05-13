from aiogram import F
from aiogram_dialog import Window
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

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static.templates import achievements_list
from fanfan.presentation.tgbot.ui import strings

from .constants import ID_ACHIEVEMENTS_SCROLL
from .getters import achievements_getter

achievements_window = Window(
    Title(
        Case(
            texts={
                True: Const("🏆 Твои достижения"),
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
