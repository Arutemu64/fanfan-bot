from aiogram.types import InlineKeyboardButton

from fanfan.core.dto.mailing import MailingId
from fanfan.core.models.feedback import FeedbackId
from fanfan.core.models.schedule_change import ScheduleChangeId
from fanfan.core.models.user import UserId
from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMessageCallback,
    OpenSubscriptionsCallback,
    ProcessFeedbackCallback,
    PullDialogDownCallback,
    ShowMailingInfoCallback,
    ShowUserInfoCallback,
    UndoScheduleChangeCallback,
)
from fanfan.presentation.tgbot.static import strings

DELETE_BUTTON = InlineKeyboardButton(
    text="🗑️ Прочитано",
    callback_data=DeleteMessageCallback().pack(),
)
OPEN_SUBSCRIPTIONS_BUTTON = InlineKeyboardButton(
    text="🔔 Настройки уведомлений",
    callback_data=OpenSubscriptionsCallback().pack(),
)
PULL_DOWN_DIALOG = InlineKeyboardButton(
    text="⏬ Опустить меню",
    callback_data=PullDialogDownCallback().pack(),
)


def show_mailing_info_button(mailing_id: MailingId) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="📃 Информация о рассылке",
        callback_data=ShowMailingInfoCallback(mailing_id=mailing_id).pack(),
    )


def process_feedback_button(feedback_id: FeedbackId) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="🙋 Беру на себя",
        callback_data=ProcessFeedbackCallback(feedback_id=feedback_id).pack(),
    )


def show_user_info_button(user_id: UserId) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=strings.titles.user_manager,
        callback_data=ShowUserInfoCallback(user_id=user_id).pack(),
    )


def undo_schedule_change_button(
    schedule_change_id: ScheduleChangeId,
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="♻️ Отменить изменение",
        callback_data=UndoScheduleChangeCallback(
            schedule_change_id=schedule_change_id
        ).pack(),
    )
