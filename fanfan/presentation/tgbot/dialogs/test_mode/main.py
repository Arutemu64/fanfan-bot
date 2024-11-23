from typing import TYPE_CHECKING

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const

from fanfan.application.quest.reset_quest import ResetQuest
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

if TYPE_CHECKING:
    from dishka import AsyncContainer


async def reset_quest_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    reset_quest: ResetQuest = await container.get(ResetQuest)
    await reset_quest()
    await callback.answer("✅ Достижения сброшены, очки обнулены")


test_mode_main_window = Window(
    Title(Const(strings.titles.test_mode)),
    Button(
        Const("🏆 Сбросить достижения"), id="reset_quest", on_click=reset_quest_handler
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.TestMode.main,
)
