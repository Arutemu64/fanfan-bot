import json
from typing import List, Optional

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
from pydantic import BaseModel, TypeAdapter, field_validator

from fanfan.presentation.tgbot import STATIC_DIR
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ACTIVITIES_DIR = STATIC_DIR / "activities"
ID_ACTIVITIES_SCROLL = "activities_scroll"


class Activity(BaseModel):
    title: str
    description: str
    where: Optional[str] = None
    image_filename: str

    @field_validator("image_filename")
    @classmethod
    def check_if_image_exists(cls, v: str):
        assert ACTIVITIES_DIR.joinpath(
            v
        ).exists(), f"Activity image {v} not found at {ACTIVITIES_DIR}"
        return v


with ACTIVITIES_DIR.joinpath("activities.json").open(encoding="utf-8") as f:
    ta = TypeAdapter(List[Activity])
    activities = ta.validate_json(json.dumps(json.load(f)))


async def activity_getter(dialog_manager: DialogManager, **kwargs):
    activity = activities[await dialog_manager.find(ID_ACTIVITIES_SCROLL).get_page()]
    return {
        "pages": len(activities),
        "title": activity.title,
        "description": activity.description,
        "where": activity.where,
        "image_filepath": ACTIVITIES_DIR.joinpath(activity.image_filename),
    }


activity_window = Window(
    Title(Format("{title}")),
    Format("{description}"),
    Format("\n<b>Где:</b> {where}", when=F["where"]),
    StaticMedia(path=Format("{image_filepath}")),
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
    SwitchTo(Const(strings.buttons.back), "main_menu", states.MAIN.HOME),
    state=states.MAIN.ACTIVITIES,
    getter=activity_getter,
)
