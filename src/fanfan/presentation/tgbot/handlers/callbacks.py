from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.feedback.proceed_feedback import (
    ProceedFeedback,
    ProceedFeedbackDTO,
)
from fanfan.application.schedule.management.revert_change import RevertScheduleChange
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.mailing.view_mailing import show_mailing_info
from fanfan.presentation.tgbot.dialogs.user_manager import start_user_manager
from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMessageCallback,
    OpenSubscriptionsCallback,
    ProcessFeedbackCallback,
    PullDialogDownCallback,
    ShowMailingInfoCallback,
    ShowUserInfoCallback,
    UndoScheduleChangeCallback,
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
) -> None:
    await show_mailing_info(dialog_manager, callback_data.mailing_id)


@router.callback_query(OpenSubscriptionsCallback.filter())
async def open_subscriptions_menu(
    query: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(
        state=states.Schedule.SUBSCRIPTIONS,
        show_mode=ShowMode.SEND,
    )


@router.callback_query(PullDialogDownCallback.filter())
async def pull_down_menu(query: CallbackQuery, dialog_manager: DialogManager) -> None:
    await dialog_manager.update(data={}, show_mode=ShowMode.SEND)


@router.callback_query(ProcessFeedbackCallback.filter())
@inject
async def process_feedback(
    query: CallbackQuery,
    callback_data: ProcessFeedbackCallback,
    interactor: FromDishka[ProceedFeedback],
):
    await interactor(ProceedFeedbackDTO(feedback_id=callback_data.feedback_id))
    await query.answer(
        "✅ Вы взяли отзыв в работу. "
        "Теперь можете связаться с пользователем. "
        "Это можно сделать в ЛС или от имени бота "
        "через информацию о пользователе (односторонняя связь). ",
        show_alert=True,
    )


@router.callback_query(ShowUserInfoCallback.filter())
@inject
async def show_user_info(
    query: CallbackQuery,
    callback_data: ShowUserInfoCallback,
    dialog_manager: DialogManager,
):
    await start_user_manager(manager=dialog_manager, user_id=callback_data.user_id)


@router.callback_query(UndoScheduleChangeCallback.filter())
@inject
async def undo_schedule_change(
    query: CallbackQuery,
    callback_data: UndoScheduleChangeCallback,
    interactor: FromDishka[RevertScheduleChange],
):
    await interactor(callback_data.schedule_change_id)
    await query.answer()
