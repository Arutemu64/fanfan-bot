import enum


class UserRole(enum.IntEnum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    VISITOR = (0, "Зритель")
    HELPER = (1, "Волонтёр")
    ORG = (2, "Организатор")
