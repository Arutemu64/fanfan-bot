import random

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.ui import images, strings
from src.db import Database
from src.redis.global_settings import GlobalSettings


async def main_menu_getter(
    dialog_manager: DialogManager, settings: GlobalSettings, db: Database, **kwargs
):
    user_data = await dialog_manager.middleware_data["state"].get_data()
    dialog_manager.dialog_data["voting_enabled"] = await settings.voting_enabled.get()
    return {
        "name": dialog_manager.event.from_user.first_name,
        "is_helper": user_data["user_role"] in [UserRole.HELPER, UserRole.ORG],
        "is_org": user_data["user_role"] == UserRole.ORG,
        "random_quote": random.choice(strings.quotes),
        "voting_enabled": dialog_manager.dialog_data["voting_enabled"],
    }


async def open_voting(callback: CallbackQuery, button: Button, manager: DialogManager):
    if manager.dialog_data.get("voting_enabled"):
        await manager.start(state=states.VOTING.NOMINATIONS)
    else:
        await callback.answer(strings.errors.voting_disabled, show_alert=True)


main = Window(
    Const("<b>📃 Главное меню</b>"),
    Const(text=" "),
    Format(strings.menus.main_menu_text),
    Const(text=" "),
    Format("<i>{random_quote}</i>"),
    StaticMedia(path=images.main_menu.absolute().__str__()),
    Row(
        Start(
            text=Const(strings.buttons.show_schedule),
            id="open_schedule",
            state=states.SCHEDULE.MAIN,
        ),
        SwitchTo(
            Const(strings.buttons.activities_menu),
            id="open_activities",
            state=states.MAIN.ACTIVITIES,
        ),
    ),
    Button(
        text=Case(
            texts={
                True: Const(strings.buttons.voting),
                False: Const(strings.buttons.voting_locked),
            },
            selector=F["voting_enabled"],
        ),
        id="open_voting",
        on_click=open_voting,
    ),
    Row(
        Start(
            text=Const(strings.buttons.helper_menu),
            id="open_helper_menu",
            when="is_helper",
            state=states.HELPER.MAIN,
        ),
        Start(
            text=Const(strings.buttons.org_menu),
            id="open_org_menu",
            state=states.ORG.MAIN,
            when="is_org",
        ),
    ),
    Start(
        text=Const("⚙️ Настройки"),
        id="open_settings",
        state=states.SETTINGS.MAIN,
    ),
    state=states.MAIN.MAIN,
    getter=main_menu_getter,
)
