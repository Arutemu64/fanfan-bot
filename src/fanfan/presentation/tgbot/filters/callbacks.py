from aiogram.filters.callback_data import CallbackData

from fanfan.core.vo.mailing import MailingId
from fanfan.core.vo.schedule_change import ScheduleChangeId
from fanfan.core.vo.user import UserId


class DeleteMessageCallback(CallbackData, prefix="delete_message"):
    pass


class ShowMailingInfoCallback(CallbackData, prefix="delete_mailing"):
    mailing_id: MailingId


class OpenSubscriptionsCallback(CallbackData, prefix="open_subscriptions"):
    pass


class PullDialogDownCallback(CallbackData, prefix="pull_dialog_down"):
    pass


class ShowUserInfoCallback(CallbackData, prefix="show_user_info"):
    user_id: UserId


class UndoScheduleChangeCallback(CallbackData, prefix="undo_schedule_change"):
    schedule_change_id: ScheduleChangeId
