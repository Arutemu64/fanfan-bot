from aiogram.filters.callback_data import CallbackData

from fanfan.core.dto.mailing import MailingId
from fanfan.core.models.feedback import FeedbackId


class DeleteMessageCallback(CallbackData, prefix="delete_message"):
    pass


class ShowMailingInfoCallback(CallbackData, prefix="delete_mailing"):
    mailing_id: MailingId


class OpenSubscriptionsCallback(CallbackData, prefix="open_subscriptions"):
    pass


class PullDialogDownCallback(CallbackData, prefix="pull_dialog_down"):
    pass


class ProcessFeedbackCallback(CallbackData, prefix="process_feedback"):
    feedback_id: FeedbackId
