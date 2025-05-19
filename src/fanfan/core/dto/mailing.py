import enum
from dataclasses import dataclass
from typing import NewType

from fanfan.core.vo.user import UserId

MailingId = NewType("MailingId", str)


class MailingStatus(enum.StrEnum):
    PENDING = (enum.auto(), "В процессе...")
    DONE = (enum.auto(), "Завершена")
    CANCELLED = (enum.auto(), "Отменена")

    def __new__(cls, value, label):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self):
        return self.label


@dataclass(slots=True, kw_only=True, frozen=True)
class MailingDTO:
    id: MailingId
    total_messages: int
    messages_processed: int
    is_cancelled: bool
    by_user_id: UserId
