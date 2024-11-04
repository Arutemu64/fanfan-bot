import enum


class BotMode(enum.StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"


class UserRole(enum.IntEnum):
    VISITOR = (10, "Зритель", "Зрители")
    PARTICIPANT = (20, "Участник", "Участники")
    HELPER = (30, "Волонтёр", "Волонтёры")
    ORG = (40, "Организатор", "Организаторы")

    def __new__(cls, value: int, label: str, label_plural: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.label_plural = label_plural
        return obj
