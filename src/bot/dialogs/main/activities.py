import json
from pathlib import Path

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
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs import states
from src.bot.ui import strings

ID_ACTIVITIES_SCROLL = "activities_scroll"

path_to_activities_folder = Path(__file__).parents[2] / "ui" / "activities"
activities_json = path_to_activities_folder / "activities.json"
with open(activities_json, mode="r") as f:
    activities = json.load(f)


async def get_activity(dialog_manager: DialogManager, **kwargs):
    pages = len(activities)
    current_activity = await dialog_manager.find(ID_ACTIVITIES_SCROLL).get_page()
    activity_title = activities[current_activity].get("title", "%title%")
    activity_text = activities[current_activity].get("text", "%text%")
    activity_where = activities[current_activity].get("where", "%where%")
    return {
        "pages": pages,
        "activity_title": activity_title,
        "activity_text": activity_text,
        "activity_where": activity_where,
    }


activity = Window(
    Format("<b>{activity_title}</b>"),
    Const(" "),
    Format("{activity_text}"),
    Const(" "),
    Format("<b>Где:</b> {activity_where}"),
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
    SwitchTo(Const(strings.buttons.back), "mm", states.MAIN.MAIN),
    state=states.MAIN.ACTIVITIES,
    getter=get_activity,
)
