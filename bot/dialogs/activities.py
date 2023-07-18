import json
from pathlib import Path

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs import states
from bot.ui.strings import buttons

path_to_activities_folder = Path(__file__).parents[1] / "ui" / "activities"
activities_json = path_to_activities_folder / "activities.json"
with open(activities_json, mode="r") as f:
    activities = json.load(f)


async def get_activity(dialog_manager: DialogManager, session: AsyncSession, **kwargs):
    if dialog_manager.dialog_data.get("current_activity"):
        activity_id = dialog_manager.dialog_data.get("current_activity")
    else:
        activity_id = 0
        dialog_manager.dialog_data["current_activity"] = activity_id
    dialog_manager.dialog_data["total_activities"] = len(activities)
    return {
        "activity_title": activities[activity_id].get("title", "%title%"),
        "activity_text": activities[activity_id].get("text", "%text%"),
        "activity_where": activities[activity_id].get("where", "%where%"),
        "activity_page": activity_id + 1,
        "total_activities": len(activities),
        "is_first_page": activity_id == 0,
        "is_last_page": activity_id + 1 == len(activities),
    }


async def change_page(callback: CallbackQuery, button: Button, manager: DialogManager):
    match button.widget_id:
        case "first":
            manager.dialog_data["current_activity"] = 0
        case "previous":
            manager.dialog_data["current_activity"] -= 1
        case "next":
            manager.dialog_data["current_activity"] += 1
        case "last":
            manager.dialog_data["current_activity"] = (
                manager.dialog_data["total_activities"] - 1
            )
    await manager.update(data=manager.dialog_data)


activity = Window(
    Format("<b>{activity_title}</b>"),
    Const(" "),
    Format("{activity_text}"),
    Const(" "),
    Format("<b>Где:</b> {activity_where}"),
    Row(
        Button(
            text=Const("⏪"), id="first", on_click=change_page, when=~F["is_first_page"]
        ),
        Button(text=Const("  "), id="first_dummy", when=F["is_first_page"]),
        Button(
            text=Const("◀️"),
            id="previous",
            on_click=change_page,
            when=~F["is_first_page"],
        ),
        Button(text=Const("  "), id="previous_dummy", when=F["is_first_page"]),
        Button(text=Format("{activity_page}/{total_activities}"), id="pager"),
        Button(
            text=Const("▶️"), id="next", on_click=change_page, when=~F["is_last_page"]
        ),
        Button(text=Const("  "), id="next_dummy", when=F["is_last_page"]),
        Button(
            text=Const("⏭️"), id="last", on_click=change_page, when=~F["is_last_page"]
        ),
        Button(text=Const("  "), id="last_dummy", when=F["is_last_page"]),
    ),
    Start(text=Const(buttons.back), id="mm", state=states.MAIN.MAIN),
    state=states.ACTIVITIES.MAIN,
    getter=get_activity,
)

dialog = Dialog(activity)
