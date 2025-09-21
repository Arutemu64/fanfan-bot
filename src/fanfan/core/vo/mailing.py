import enum
from typing import NewType

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
