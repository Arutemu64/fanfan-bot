from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMailingCallback,
    DeleteMessageCallback,
    OpenSubscriptionsCallback,
    PullDialogDownCallback,
)

router = Router(name="callbacks_router")


@router.callback_query(DeleteMessageCallback.filter())
async def delete_message(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer("⚠️ Этому сообщению больше 2 дней, удалите его вручную")


@router.callback_query(DeleteMailingCallback.filter())
@inject
async def delete_mailing_callback(
    query: CallbackQuery,
    callback_data: DeleteMailingCallback,
    notifier: FromDishka[Notifier],
) -> None:
    mailing_info = await notifier.delete_mailing(callback_data.mailing_id)
    await query.answer(
        text=f"✅ Будет удалено {mailing_info.count} уведомлений",
        show_alert=True,
    )


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
