from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Case, Const

from src.bot.dialogs import states
from src.bot.structures import Settings
from src.bot.ui import strings


async def getter(settings: Settings, **kwargs):
    voting_enabled = await settings.voting_enabled.get()
    return {"voting_enabled": voting_enabled}


async def switch_voting(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    settings: Settings = manager.middleware_data["settings"]
    await settings.voting_enabled.set(not await settings.voting_enabled.get())


org_menu = Window(
    Const("<b>🔧 Меню организатора</b>"),
    Const(" "),
    SwitchTo(
        state=states.ORG.ASK_USERNAME,
        id="edit_user",
        text=Const("👤✏️ Редактировать пользователя"),
    ),
    SwitchTo(
        state=states.ORG.NEW_TICKET,
        id="new_ticket",
        text=Const("🎫 Добавить новый билет"),
    ),
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
    Cancel(Const(strings.buttons.back)),
    state=states.ORG.MAIN,
    getter=getter,
)
