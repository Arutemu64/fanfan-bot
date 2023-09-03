import enum


class UserRole(enum.StrEnum):
    VISITOR = "visitor"
    HELPER = "helper"
    ORG = "org"

    @classmethod
    def get_role_name(cls, role: str) -> str:
        match role:
            case cls.VISITOR:
                return "Зритель"
            case cls.HELPER:
                return "Волонтёр"
            case cls.ORG:
                return "Организатор"
