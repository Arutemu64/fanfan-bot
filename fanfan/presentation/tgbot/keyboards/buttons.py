from aiogram.types import InlineKeyboardButton

from fanfan.core.models.mailing import MailingId
from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMessageCallback,
    OpenSubscriptionsCallback,
    PullDialogDownCallback,
    ShowMailingInfoCallback,
)

DELETE_BUTTON = InlineKeyboardButton(
    text="🗑️ Прочитано",
    callback_data=DeleteMessageCallback().pack(),
)
OPEN_SUBSCRIPTIONS_BUTTON = InlineKeyboardButton(
    text="🔔 Настройки уведомлений",
    callback_data=OpenSubscriptionsCallback().pack(),
)
PULL_DOWN_DIALOG = InlineKeyboardButton(
    text="🔽 Опустить меню",
    callback_data=PullDialogDownCallback().pack(),
)


def show_mailing_info_button(mailing_id: MailingId) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="📃 Информация о рассылке",
        callback_data=ShowMailingInfoCallback(mailing_id=mailing_id).pack(),
    )