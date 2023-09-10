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
from src.bot.dialogs.widgets import Title
from src.bot.structures.userdata import UserData
from src.bot.ui import strings
from src.db import Database

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"

# fmt: off
AchievementsList = Jinja(  # noqa
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
    user_data: UserData = await dialog_manager.middleware_data["state"].get_data()
    current_page = await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page()
    pages = await db.achievement.get_number_of_pages(user_data["items_per_page"])
    if pages == 0:
        pages = 1
    results = await db.achievement.get_achievements_page(
        page=current_page,
        achievements_per_page=user_data["items_per_page"],
        user_id=dialog_manager.event.from_user.id,
    )
    if results:
        achievements, received_achievements = zip(*results)
    else:
        achievements, received_achievements = [], []
    return {
        "achievements": achievements,
        "received_achievements": received_achievements,
        "pages": pages,
    }


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
