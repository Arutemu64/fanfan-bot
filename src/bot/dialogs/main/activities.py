import json

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
from aiogram_dialog.widgets.text import Const, Format, Jinja

from src.bot import BOT_ROOT_DIR
from src.bot.dialogs import states
from src.bot.ui import images, strings

ID_ACTIVITIES_SCROLL = "activities_scroll"

activities_json = BOT_ROOT_DIR / "ui/activities.json"
with open(activities_json, mode="r", encoding="utf-8") as f:
    activities = json.load(f)


async def activity_getter(dialog_manager: DialogManager, **kwargs):
    pages = len(activities)
    current_activity = await dialog_manager.find(ID_ACTIVITIES_SCROLL).get_page()
    activity_title = activities[current_activity].get("title", "%title%")
    activity_text = activities[current_activity].get("text", "%text%")
    activity_where = activities[current_activity].get("where")
    activity_image = (
        images.activities.joinpath(activities[current_activity].get("image"))
        .absolute()
        .__str__()
    )
    return {
        "pages": pages,
        "activity_title": activity_title,
        "activity_text": activity_text,
        "activity_where": activity_where,
        "activity_image": activity_image,
    }


# fmt: off
activity_html = Jinja(
    "<b>{{ activity_title|upper }}</b>"
    "\n\n"
    "{{ activity_text }}"
    "\n\n"
    "{% if activity_where %}"
        "<b>Где:</b> {{ activity_where }}"
    "{% endif %}"
)
# fmt: on


activity = Window(
    activity_html,
    StaticMedia(path=Format("{activity_image}")),
    StubScroll(id=ID_ACTIVITIES_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACTIVITIES_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACTIVITIES_SCROLL, text=Const("⏭️")),
    ),
    SwitchTo(Const(strings.buttons.back), "main_menu", states.MAIN.MAIN),
    state=states.MAIN.ACTIVITIES,
    getter=activity_getter,
)
