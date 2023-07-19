import random

from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Row, Start, Url
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs import states
from src.bot.ui import strings
from src.config import conf
from src.db.models import User


async def getter(user: User, **kwargs):
    is_helper = user.role == "helper"
    is_org = user.role == "org"
    if is_org:
        is_helper = True
    random_quote = random.choice(strings.quotes)
    return {"is_helper": is_helper, "is_org": is_org, "random_quote": random_quote}


main_menu = Window(
    Const("<b>📃 Главное меню</b>"),
    Const(text=" "),
    Format(strings.menus.main_menu_text),
    Const(text=" "),
    Format("{random_quote}"),
    Url(
        text=Const(strings.buttons.changelog_channel),
        url=Const("https://t.me/fanfan_bot_dev_notes"),
    ),
    Url(
        text=Const(strings.buttons.notifications_channel),
        url=Const(conf.bot.channel_link),
    ),
    Row(
        Start(
            text=Const(strings.buttons.show_schedule),
            state=states.SCHEDULE.MAIN,
            id="schedule",
            data={"back_to": states.MAIN.MAIN},
        ),
        Start(
            Const(strings.buttons.activities_menu),
            id="activities",
            state=states.ACTIVITIES.MAIN,
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
            state=states.HELPER.MAIN,
        ),
        Start(
            text=Const(strings.buttons.org_menu),
            id="org_menu",
            when="is_org",
            state=states.ORG.MAIN,
        ),
    ),
    state=states.MAIN.MAIN,
    getter=getter,
)

dialog = Dialog(main_menu, launch_mode=LaunchMode.ROOT)
