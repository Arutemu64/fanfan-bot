from typing import TYPE_CHECKING

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.quest.cancel_registration import CancelRegistration
from fanfan.core.exceptions.base import AppException
from fanfan.presentation.tgbot import states

if TYPE_CHECKING:
    from dishka import AsyncContainer


async def cancel_registration_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    cancel: CancelRegistration = await container.get(CancelRegistration)

    try:
        await cancel()
        await callback.answer("✅ Регистрация на квест отменена")
        await manager.switch_to(state=states.Quest.main)
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return


cancel_registration_window = Window(
    Const(
        "⚠️ Отменить регистрацию на квест? "
        "Возможно, зарегистрироваться больше не получится..."
    ),
    Button(
        Const("⚠️ Да, отменить регистрацию"),
        id="cancel_registration",
        on_click=cancel_registration_handler,
    ),
    SwitchTo(Const("😥 Нет, я передумал"), id="back_to_main", state=states.Quest.main),
    state=states.Quest.cancel_registration,
)
