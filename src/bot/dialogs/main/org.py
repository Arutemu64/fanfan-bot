from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Case, Const

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database


async def getter(db: Database, **kwargs):
    voting_enabled = (await db.settings.get_by_where(True)).voting_enabled
    return {"voting_enabled": voting_enabled}


async def switch_voting(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data.get("db")
    settings = await db.settings.get_by_where(True)
    settings.voting_enabled = not settings.voting_enabled
    await db.session.commit()


org_menu = Window(
    Const("<b>🔧 Меню организатора</b>"),
    Const(" "),
    Const(strings.menus.org_menu_text),
    Button(
        text=Case(
            texts={
                True: Const(strings.buttons.disable_voting),
                False: Const(strings.buttons.enable_voting),
            },
            selector=F["voting_enabled"],
        ),
        id="switch_voting_button",
        on_click=switch_voting,
    ),
    SwitchTo(Const(strings.buttons.back), "mm", states.MAIN.MAIN),
    state=states.MAIN.ORG,
    getter=getter,
)
