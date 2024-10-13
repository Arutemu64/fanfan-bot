import enum
from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

MailingId = NewType("MailingId", str)


class MailingStatus(enum.StrEnum):
    PENDING = ("pending", "В процессе...")
    DONE = ("done", "Завершена")
    DELETED = ("deleted", "Удалена")

    def __new__(cls, value, label):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj


@dataclass(frozen=True, slots=True)
class MailingData:
    id: MailingId
    total: int
    sent: int
    status: MailingStatus
    by_user_id: UserId
