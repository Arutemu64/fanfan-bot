from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import inject

from fanfan.presentation.tgbot.dialogs.mailing.api import show_mailing_info
from fanfan.presentation.tgbot.filters.callbacks import ShowMailingInfoCallback

mailing_handlers_router = Router(name="mailing_handlers_router")


@mailing_handlers_router.callback_query(ShowMailingInfoCallback.filter())
@inject
async def show_mailing_info_callback(
    query: CallbackQuery,
    callback_data: ShowMailingInfoCallback,
    dialog_manager: DialogManager,
) -> None:
    await show_mailing_info(dialog_manager, callback_data.mailing_id)
