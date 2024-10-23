import enum


class BotMode(enum.StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"


class UserRole(enum.StrEnum):
    VISITOR = ("visitor", "Зритель", "Зрители")
    PARTICIPANT = ("participant", "Участник", "Участники")
    HELPER = ("helper", "Волонтёр", "Волонтёры")
    ORG = ("org", "Организатор", "Организаторы")

    def __new__(cls, value: str, label: str, label_plural: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.label_plural = label_plural
        return obj
