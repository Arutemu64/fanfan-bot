import enum


class BotMode(enum.StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"


class QRType(enum.StrEnum):
    ACHIEVEMENT = "achievement"


class UserRole(enum.StrEnum):
    def __new__(cls, value, label, label_plural):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.label_plural = label_plural
        return obj

    VISITOR = ("visitor", "Зритель", "Зрители")
    PARTICIPANT = ("participant", "Участник", "Участники")
    HELPER = ("helper", "Волонтёр", "Волонтёры")
    ORG = ("org", "Организатор", "Организаторы")
