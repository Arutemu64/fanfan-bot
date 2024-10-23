from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.adapters.utils.notifier import Notifier
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.mailing.mailing_info import show_mailing_info
from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMessageCallback,
    OpenSubscriptionsCallback,
    PullDialogDownCallback,
    ShowMailingInfoCallback,
)

router = Router(name="callbacks_router")


@router.callback_query(DeleteMessageCallback.filter())
async def delete_message(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer("⚠️ Этому сообщению больше 2 дней, удалите его вручную")


@router.callback_query(ShowMailingInfoCallback.filter())
@inject
async def show_mailing_info_callback(
    query: CallbackQuery,
    callback_data: ShowMailingInfoCallback,
    dialog_manager: DialogManager,
    notifier: FromDishka[Notifier],
) -> None:
    await show_mailing_info(dialog_manager, callback_data.mailing_id)


@router.callback_query(OpenSubscriptionsCallback.filter())
async def open_subscriptions_menu(
    query: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(
        state=states.Schedule.subscriptions,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@router.callback_query(PullDialogDownCallback.filter())
async def pull_down_menu(query: CallbackQuery, dialog_manager: DialogManager) -> None:
    await dialog_manager.update(data={}, show_mode=ShowMode.DELETE_AND_SEND)
