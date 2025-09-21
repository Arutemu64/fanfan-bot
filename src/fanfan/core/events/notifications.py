from dataclasses import dataclass

from aiogram.types import Message

from fanfan.core.dto.notification import UserNotification
from fanfan.core.events.base import AppEvent
from fanfan.core.vo.mailing import MailingId
from fanfan.core.vo.user import UserId, UserRole


@dataclass(kw_only=True, slots=True)
class NewNotificationEvent(AppEvent):
    subject: str = "notifications.new"

    user_id: UserId
    notification: UserNotification
    mailing_id: MailingId | None = None

    def __post_init__(self):
        if self.mailing_id:
            self.subject = f"notifications.mailing.{self.mailing_id}"


@dataclass(kw_only=True, slots=True)
class NewRolesNotificationEvent(AppEvent):
    subject: str = "notifications.roles.new"

    notification: UserNotification
    roles: list[UserRole]
    mailing_id: MailingId


@dataclass(kw_only=True, slots=True)
class EditNotificationEvent(AppEvent):
    subject: str = "notifications.edit"

    message: Message
    notification: UserNotification
    mailing_id: MailingId | None


@dataclass(kw_only=True, slots=True)
class CancelMailingEvent(AppEvent):
    subject: str = "notification.mailing.cancel"

    mailing_id: MailingId
