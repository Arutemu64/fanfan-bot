import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.quest.reset_quest import ResetQuest
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
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


dev_settings_window = Window(
    Title(Const(strings.titles.dev_settings)),
    Button(
        Const("🏆 Сбросить свой прогресс квеста"),
        id="reset_quest",
        on_click=reset_quest_handler,
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Settings.MAIN, id="back"),
    state=states.Settings.DEV_SETTINGS,
)
