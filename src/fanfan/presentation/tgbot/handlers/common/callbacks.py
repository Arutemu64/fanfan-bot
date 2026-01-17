from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode

from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMessageCallback,
    PullDialogDownCallback,
)

common_callbacks_router = Router(name="common_callbacks_router")


@common_callbacks_router.callback_query(DeleteMessageCallback.filter())
async def delete_message(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer("⚠️ Этому сообщению больше 2 дней, удалите его вручную")


@common_callbacks_router.callback_query(PullDialogDownCallback.filter())
async def pull_down_menu(query: CallbackQuery, dialog_manager: DialogManager) -> None:
    await dialog_manager.update(data={}, show_mode=ShowMode.SEND)
