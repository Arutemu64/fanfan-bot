from aiogram.filters.callback_data import CallbackData


class DeleteMessageCallback(CallbackData, prefix="delete_message"):
    pass


class DeleteMailingCallback(CallbackData, prefix="delete_mailing"):
    mailing_id: str


class OpenSubscriptionsCallback(CallbackData, prefix="open_subscriptions"):
    pass


class PullDialogDownCallback(CallbackData, prefix="pull_dialog_down"):
    pass
