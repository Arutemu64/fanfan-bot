from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.quest.reset_quest import ResetQuest
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


@inject
async def reset_quest_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    reset_quest: FromDishka[ResetQuest],
) -> None:
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
