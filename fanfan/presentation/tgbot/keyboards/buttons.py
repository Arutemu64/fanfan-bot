from aiogram.types import InlineKeyboardButton

from fanfan.presentation.tgbot.filters.callbacks import (
    DeleteMailingCallback,
    DeleteMessageCallback,
    OpenSubscriptionsCallback,
    PullDialogDownCallback,
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


def get_delete_mailing_button(mailing_id: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="🗑️ Отменить рассылку",
        callback_data=DeleteMailingCallback(mailing_id=mailing_id).pack(),
    )
