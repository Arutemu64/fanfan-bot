from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.feedback.process_feedback import (
    ProcessFeedback,
    ProcessFeedbackDTO,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.mailing.mailing_info import show_mailing_info
from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMessageCallback,
    OpenSubscriptionsCallback,
    ProcessFeedbackCallback,
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
    await dialog_manager.update(data={}, show_mode=ShowMode.SEND)


@router.callback_query(ProcessFeedbackCallback.filter())
@inject
async def process_feedback(
    query: CallbackQuery,
    callback_data: ProcessFeedbackCallback,
    interactor: FromDishka[ProcessFeedback],
    dialog_manager: DialogManager,
):
    feedback = await interactor(
        ProcessFeedbackDTO(feedback_id=callback_data.feedback_id)
    )
    await query.answer(
        "✅ Вы взяли обработку отзыва на себя. "
        f"Теперь можете связаться с @{feedback.user.username} "
        f"в ЛС для уточнения деталей. "
        "Другие организаторы увидят, что вы взяли отзыв в работу.",
        show_alert=True,
    )
