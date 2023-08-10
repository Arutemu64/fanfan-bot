import math
import random

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo, Url
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs import states
from src.bot.structures import Role
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Event, User

per_page = conf.bot.events_per_page


async def getter(dialog_manager: DialogManager, user: User, **kwargs):
    name = dialog_manager.event.from_user.first_name
    is_helper = user.role == Role.HELPER
    is_org = user.role == Role.ORG
    if is_org:
        is_helper = True
    random_quote = random.choice(strings.quotes)
    return {
        "name": name,
        "is_helper": is_helper,
        "is_org": is_org,
        "random_quote": random_quote,
    }


async def open_schedule(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_by_where(Event.current == True)  # noqa
    if current_event:
        current_event_id = current_event.id
    else:
        current_event_id = 1
    current_page = math.floor((current_event_id - 1) / per_page)
    await manager.start(state=states.SCHEDULE.MAIN, data={"current_page": current_page})


main = Window(
    Const("<b>📃 Главное меню</b>"),
    Const(text=" "),
    Format(strings.menus.main_menu_text),
    Const(text=" "),
    Format("<i>{random_quote}</i>"),
    Url(
        text=Const(strings.buttons.changelog_channel),
        url=Const("https://t.me/fanfan_bot_dev_notes"),
    ),
    Row(
        Button(
            text=Const(strings.buttons.show_schedule),
            id="schedule",
            on_click=open_schedule,
        ),
        SwitchTo(
            Const(strings.buttons.activities_menu),
            id="activities",
            state=states.MAIN.ACTIVITIES,
        ),
    ),
    Start(
        text=Const(strings.buttons.voting), state=states.VOTING.NOMINATIONS, id="voting"
    ),
    Row(
        Start(
            text=Const(strings.buttons.helper_menu),
            id="helper_menu",
            when="is_helper",
            state=states.MAIN.HELPER,
        ),
        Start(
            text=Const(strings.buttons.org_menu),
            id="org_menu",
            when="is_org",
            state=states.MAIN.ORG,
        ),
    ),
    state=states.MAIN.MAIN,
    getter=getter,
)
