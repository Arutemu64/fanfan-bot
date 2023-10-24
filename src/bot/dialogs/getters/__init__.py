from ...structures import UserRole
from .achievements import achievements_list
from .schedule import schedule_list


async def get_roles(**kwargs) -> dict:
    return {
        "roles": list(
            map(lambda item: (item.value, item.label, item.label_plural), UserRole)
        )
    }


__all__ = ["achievements_list", "schedule_list", "get_roles"]
