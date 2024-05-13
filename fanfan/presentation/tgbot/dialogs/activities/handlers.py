from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from fanfan.presentation.tgbot import states

from .constants import DATA_SELECTED_ACTIVITY_ID


async def select_activity_handler(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: int,
):
    dialog_manager.dialog_data[DATA_SELECTED_ACTIVITY_ID] = item_id
    await dialog_manager.switch_to(states.ACTIVITIES.ACTIVITY_INFO)
