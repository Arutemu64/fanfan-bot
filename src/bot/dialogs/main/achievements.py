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

from src.bot.dialogs import states
from src.bot.dialogs.getters import achievements_list
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings
from src.db import Database

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"

# fmt: off
AchievementsList = Jinja(
    "{% for achievement in achievements %}"
        """<b>{{ achievement.title }}</b> {{ "✅" if achievement.id in received_achievements else "" }}\n"""  # noqa: E501
        "{% if achievement.description %}"
            "{{ achievement.description }}\n"
        "{% endif %}"
        "\n\n"
    "{% endfor %}"
)
# fmt: on


async def achievements_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    return await achievements_list(
        db=db,
        achievements_per_page=dialog_manager.dialog_data["achievements_per_page"],
        page=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page(),
        user_id=dialog_manager.event.from_user.id,
    )


achievements_window = Window(
    Title(strings.titles.achievements),
    AchievementsList,
    StubScroll(id=ID_ACHIEVEMENTS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACHIEVEMENTS_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    SwitchTo(text=Const(strings.buttons.back), state=states.MAIN.MAIN, id="back"),
    state=states.MAIN.ACHIEVEMENTS,
    getter=achievements_getter,
)
